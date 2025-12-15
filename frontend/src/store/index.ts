import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import inventoryReducer from './slices/inventorySlice'
import reservationReducer from './slices/reservationSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    inventory: inventoryReducer,
    reservations: reservationReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
