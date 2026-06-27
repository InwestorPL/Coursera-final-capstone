package com.travellist.app.repository

import com.travellist.app.data.*

class TravelRepository(
    private val tripDao: TripDao,
    private val travelItemDao: TravelItemDao
) {
    val allTrips = tripDao.getAllTrips()

    suspend fun insertTrip(trip: Trip) = tripDao.insertTrip(trip)
    suspend fun updateTrip(trip: Trip) = tripDao.updateTrip(trip)
    suspend fun deleteTrip(trip: Trip) = tripDao.deleteTrip(trip)

    fun getItemsForTrip(tripId: Long) = travelItemDao.getItemsForTrip(tripId)
    suspend fun insertItem(item: TravelItem) = travelItemDao.insertItem(item)
    suspend fun updateItem(item: TravelItem) = travelItemDao.updateItem(item)
    suspend fun deleteItem(item: TravelItem) = travelItemDao.deleteItem(item)
}
