package com.travellist.app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.travellist.app.data.Trip
import com.travellist.app.data.TravelItem
import com.travellist.app.repository.TravelRepository
import kotlinx.coroutines.launch

class TripViewModel(private val repository: TravelRepository) : ViewModel() {
    val allTrips = repository.allTrips

    fun getItemsForTrip(tripId: Long) = repository.getItemsForTrip(tripId)

    fun insertTrip(trip: Trip) = viewModelScope.launch { repository.insertTrip(trip) }
    fun deleteTrip(trip: Trip) = viewModelScope.launch { repository.deleteTrip(trip) }

    fun insertItem(item: TravelItem) = viewModelScope.launch { repository.insertItem(item) }
    fun updateItem(item: TravelItem) = viewModelScope.launch { repository.updateItem(item) }
    fun deleteItem(item: TravelItem) = viewModelScope.launch { repository.deleteItem(item) }
}
