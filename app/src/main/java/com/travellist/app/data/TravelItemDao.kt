package com.travellist.app.data

import androidx.lifecycle.LiveData
import androidx.room.*

@Dao
interface TravelItemDao {
    @Query("SELECT * FROM travel_items WHERE tripId = :tripId ORDER BY category, name")
    fun getItemsForTrip(tripId: Long): LiveData<List<TravelItem>>

    @Insert
    suspend fun insertItem(item: TravelItem): Long

    @Update
    suspend fun updateItem(item: TravelItem)

    @Delete
    suspend fun deleteItem(item: TravelItem)
}
