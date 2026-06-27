package com.travellist.app.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "travel_items")
data class TravelItem(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val tripId: Long,
    val name: String,
    val category: String,
    val isChecked: Boolean = false
)
