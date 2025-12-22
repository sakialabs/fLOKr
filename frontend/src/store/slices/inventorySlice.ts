import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { InventoryItem } from '@/lib/api-services'

interface InventoryState {
  items: InventoryItem[]
  loading: boolean
  error: string | null
}

const initialState: InventoryState = {
  items: [],
  loading: false,
  error: null,
}

const inventorySlice = createSlice({
  name: 'inventory',
  initialState,
  reducers: {
    setItems: (state, action: PayloadAction<InventoryItem[]>) => {
      state.items = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setItems, setLoading, setError } = inventorySlice.actions
export default inventorySlice.reducer
