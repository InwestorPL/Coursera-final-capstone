package com.travellist.app.adapter

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.travellist.app.data.TravelItem
import com.travellist.app.databinding.ItemTravelItemBinding

class TravelItemAdapter(
    private val onItemCheckedChange: (TravelItem, Boolean) -> Unit,
    private val onItemDelete: (TravelItem) -> Unit
) : ListAdapter<TravelItem, TravelItemAdapter.TravelItemViewHolder>(TravelItemDiffCallback()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TravelItemViewHolder =
        TravelItemViewHolder(ItemTravelItemBinding.inflate(LayoutInflater.from(parent.context), parent, false))

    override fun onBindViewHolder(holder: TravelItemViewHolder, position: Int) =
        holder.bind(getItem(position))

    inner class TravelItemViewHolder(private val binding: ItemTravelItemBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(item: TravelItem) {
            binding.cbItem.setOnCheckedChangeListener(null)
            binding.cbItem.text = item.name
            binding.tvCategory.text = item.category
            binding.cbItem.isChecked = item.isChecked
            binding.cbItem.setOnCheckedChangeListener { _, isChecked ->
                onItemCheckedChange(item, isChecked)
            }
            binding.btnDeleteItem.setOnClickListener { onItemDelete(item) }
        }
    }

    class TravelItemDiffCallback : DiffUtil.ItemCallback<TravelItem>() {
        override fun areItemsTheSame(oldItem: TravelItem, newItem: TravelItem) = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: TravelItem, newItem: TravelItem) = oldItem == newItem
    }
}
