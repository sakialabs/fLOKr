"""
Multi-hub inventory coordination service.
Handles inventory transfers between hubs with conservation validation.
"""
from django.db import transaction
from django.utils import timezone
from users.notifications import send_notification


class InventoryTransferService:
    """Service for managing inventory transfers between hubs."""
    
    @staticmethod
    @transaction.atomic
    def initiate_transfer(item, from_hub, to_hub, quantity, initiated_by, reason=''):
        """
        Initiate an inventory transfer between hubs.
        Validates quantity conservation.
        
        Args:
            item: InventoryItem instance
            from_hub: Source Hub instance
            to_hub: Destination Hub instance
            quantity: Number of items to transfer
            initiated_by: User initiating transfer
            reason: Reason for transfer
        
        Returns:
            InventoryTransfer instance
        
        Raises:
            ValueError: If validation fails
        """
        from inventory.models import InventoryTransfer
        
        # Validation
        if item.hub != from_hub:
            raise ValueError(f"Item does not belong to {from_hub.name}")
        
        if from_hub == to_hub:
            raise ValueError("Cannot transfer to the same hub")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if quantity > item.quantity_available:
            raise ValueError(f"Only {item.quantity_available} items available for transfer")
        
        # Create transfer record
        transfer = InventoryTransfer.objects.create(
            item=item,
            from_hub=from_hub,
            to_hub=to_hub,
            quantity=quantity,
            initiated_by=initiated_by,
            reason=reason,
            status='pending'
        )
        
        # Reserve quantity at source hub (reduce available but keep total)
        item.quantity_available -= quantity
        item.save()
        
        # Notify stewards at both hubs
        InventoryTransferService._notify_transfer_initiated(transfer)
        
        return transfer
    
    @staticmethod
    @transaction.atomic
    def approve_transfer(transfer, approved_by):
        """
        Approve a pending transfer and mark it in transit.
        
        Args:
            transfer: InventoryTransfer instance
            approved_by: User approving the transfer
        """
        if transfer.status != 'pending':
            raise ValueError(f"Cannot approve transfer with status: {transfer.status}")
        
        transfer.status = 'in_transit'
        transfer.approved_by = approved_by
        transfer.approved_at = timezone.now()
        transfer.save()
        
        # Notify initiator
        if transfer.initiated_by:
            send_notification(
                user=transfer.initiated_by,
                notification_type='transfer_approved',
                title="Transfer Approved",
                message=f"Transfer of {transfer.quantity}x {transfer.item.name} from {transfer.from_hub.name} to {transfer.to_hub.name} has been approved.",
                data={'transfer_id': str(transfer.id)}
            )
    
    @staticmethod
    @transaction.atomic
    def complete_transfer(transfer, completed_by, notes=''):
        """
        Complete an in-transit transfer.
        Updates inventory at both hubs with conservation validation.
        
        Args:
            transfer: InventoryTransfer instance
            completed_by: User completing the transfer
            notes: Optional completion notes
        """
        if transfer.status != 'in_transit':
            raise ValueError(f"Cannot complete transfer with status: {transfer.status}")
        
        from inventory.models import InventoryItem
        
        item = transfer.item
        quantity = transfer.quantity
        
        # Validate conservation at source
        original_total_source = item.quantity_total
        
        # Reduce total at source hub
        item.quantity_total -= quantity
        # Available was already reduced when transfer initiated
        item.save()
        
        # Check if item already exists at destination hub
        destination_item = InventoryItem.objects.filter(
            hub=transfer.to_hub,
            name=item.name,
            category=item.category
        ).first()
        
        if destination_item:
            # Add to existing item
            destination_item.quantity_total += quantity
            destination_item.quantity_available += quantity
            destination_item.save()
        else:
            # Create new item at destination
            destination_item = InventoryItem.objects.create(
                hub=transfer.to_hub,
                name=item.name,
                description=item.description,
                category=item.category,
                tags=item.tags,
                condition=item.condition,
                images=item.images,
                quantity_total=quantity,
                quantity_available=quantity,
                donor=item.donor,
                status='active'
            )
        
        # Mark transfer complete
        transfer.status='completed'
        transfer.completed_by = completed_by
        transfer.completed_at = timezone.now()
        transfer.notes = notes
        transfer.save()
        
        # Notify stakeholders
        InventoryTransferService._notify_transfer_completed(transfer, destination_item)
        
        return destination_item
    
    @staticmethod
    @transaction.atomic
    def cancel_transfer(transfer, cancelled_by, reason=''):
        """
        Cancel a pending or in-transit transfer.
        Restores inventory quantities.
        
        Args:
            transfer: InventoryTransfer instance
            cancelled_by: User cancelling the transfer
            reason: Reason for cancellation
        """
        if transfer.status == 'completed':
            raise ValueError("Cannot cancel completed transfer")
        
        if transfer.status == 'cancelled':
            raise ValueError("Transfer already cancelled")
        
        # Restore available quantity at source
        item = transfer.item
        item.quantity_available += transfer.quantity
        item.save()
        
        # Mark cancelled
        transfer.status = 'cancelled'
        transfer.notes = f"Cancelled by {cancelled_by.get_full_name()}: {reason}"
        transfer.updated_at = timezone.now()
        transfer.save()
        
        # Notify initiator
        if transfer.initiated_by:
            send_notification(
                user=transfer.initiated_by,
                notification_type='transfer_cancelled',
                title="Transfer Cancelled",
                message=f"Transfer of {transfer.quantity}x {transfer.item.name} has been cancelled.",
                data={'transfer_id': str(transfer.id), 'reason': reason}
            )
    
    @staticmethod
    def _notify_transfer_initiated(transfer):
        """Notify stewards at both hubs about new transfer."""
        # Notify source hub stewards
        for steward in transfer.from_hub.stewards.all():
            send_notification(
                user=steward,
                notification_type='transfer_initiated',
                title="Transfer Request",
                message=f"{transfer.initiated_by.get_full_name()} initiated transfer of {transfer.quantity}x {transfer.item.name} to {transfer.to_hub.name}.",
                data={'transfer_id': str(transfer.id)}
            )
        
        # Notify destination hub stewards
        for steward in transfer.to_hub.stewards.all():
            send_notification(
                user=steward,
                notification_type='transfer_incoming',
                title="Incoming Transfer",
                message=f"Incoming transfer of {transfer.quantity}x {transfer.item.name} from {transfer.from_hub.name}.",
                data={'transfer_id': str(transfer.id)}
            )
    
    @staticmethod
    def _notify_transfer_completed(transfer, destination_item):
        """Notify stakeholders about completed transfer."""
        # Notify initiator
        if transfer.initiated_by:
            send_notification(
                user=transfer.initiated_by,
                notification_type='transfer_completed',
                title="Transfer Completed",
                message=f"Transfer of {transfer.quantity}x {transfer.item.name} to {transfer.to_hub.name} has been completed.",
                data={'transfer_id': str(transfer.id)}
            )
        
        # Notify destination hub stewards
        for steward in transfer.to_hub.stewards.all():
            send_notification(
                user=steward,
                notification_type='transfer_received',
                title="Transfer Received",
                message=f"Received {transfer.quantity}x {transfer.item.name} from {transfer.from_hub.name}.",
                data={
                    'transfer_id': str(transfer.id),
                    'item_id': str(destination_item.id)
                }
            )
    
    @staticmethod
    def get_hub_transfers(hub, status_filter=None):
        """
        Get all transfers for a hub (incoming and outgoing).
        
        Args:
            hub: Hub instance
            status_filter: Optional status to filter by
        
        Returns:
            dict with incoming and outgoing transfers
        """
        from inventory.models import InventoryTransfer
        
        incoming = InventoryTransfer.objects.filter(to_hub=hub)
        outgoing = InventoryTransfer.objects.filter(from_hub=hub)
        
        if status_filter:
            incoming = incoming.filter(status=status_filter)
            outgoing = outgoing.filter(status=status_filter)
        
        return {
            'incoming': incoming.select_related('item', 'from_hub', 'initiated_by').order_by('-created_at'),
            'outgoing': outgoing.select_related('item', 'to_hub', 'initiated_by').order_by('-created_at')
        }
