package com.travellist.app.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.travellist.app.data.Trip
import com.travellist.app.databinding.ItemTripBinding

class TripAdapter(
    private val onTripClick: (Trip) -> Unit,
    private val onTripDelete: (Trip) -> Unit
) : ListAdapter<Trip, TripAdapter.TripViewHolder>(TripDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TripViewHolder =
        TripViewHolder(ItemTripBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: TripViewHolder, position: Int) =
        holder.bind(getItem(position))

    inner class TripViewHolder(private val binding: ItemTripBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(trip: Trip) {
            binding.tvTripName.text = trip.name
            binding.tvDestination.text = "📍 ${trip.destination.ifEmpty { "Destino não informado" }}"
            binding.tvDepartureDate.text = "📅 ${trip.departureDate.ifEmpty { "Data não informada" }}"
            binding.root.setOnClickListener { onTripClick(trip) }
            binding.btnDeleteTrip.setOnClickListener { onTripDelete(trip) }
        }
    }

    class TripDiffCallback : DiffUtil.ItemCallback<Trip>() {
        override fun areItemsTheSame(oldItem: Trip, newItem: Trip) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: Trip, newItem: Trip) = oldItem == newItem
    }
}
