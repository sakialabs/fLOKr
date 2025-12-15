import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface ReservationState {
  reservations: any[]
  loading: boolean
  error: string | null
}

const initialState: ReservationState = {
  reservations: [],
  loading: false,
  error: null,
}

const reservationSlice = createSlice({
  name: 'reservations',
  initialState,
  reducers: {
    setReservations: (state, action: PayloadAction<any[]>) => {
      state.reservations = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setReservations, setLoading, setError } = reservationSlice.actions
export default reservationSlice.reducer
