package com.travellist.app

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.travellist.app.adapter.TravelItemAdapter
import com.travellist.app.data.AppDatabase
import com.travellist.app.data.TravelItem
import com.travellist.app.databinding.ActivityTripDetailBinding
import com.travellist.app.databinding.DialogAddItemBinding
import com.travellist.app.repository.TravelRepository
import com.travellist.app.viewmodel.TripViewModel
import com.travellist.app.viewmodel.TripViewModelFactory

class TripDetailActivity : AppCompatActivity() {
    private lateinit var binding: ActivityTripDetailBinding
    private lateinit var viewModel: TripViewModel
    private var tripId: Long = 0

    companion object {
        const val EXTRA_TRIP_ID = "extra_trip_id"
        const val EXTRA_TRIP_NAME = "extra_trip_name"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityTripDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        tripId = intent.getLongExtra(EXTRA_TRIP_ID, 0)
        title = intent.getStringExtra(EXTRA_TRIP_NAME) ?: getString(R.string.app_name)

        val db = AppDatabase.getDatabase(this)
        val repo = TravelRepository(db.tripDao(), db.travelItemDao())
        viewModel = ViewModelProvider(this, TripViewModelFactory(repo))[TripViewModel::class.java]

        val adapter = TravelItemAdapter(
            onItemCheckedChange = { item, isChecked ->
                viewModel.updateItem(item.copy(isChecked = isChecked))
            },
            onItemDelete = { item ->
                AlertDialog.Builder(this)
                    .setTitle("Remover item")
                    .setMessage("Remover \"${item.name}\"?")
                    .setPositiveButton("Remover") { _, _ -> viewModel.deleteItem(item) }
                    .setNegativeButton("Cancelar", null)
                    .show()
            }
        )

        binding.rvItems.adapter = adapter

        viewModel.getItemsForTrip(tripId).observe(this) { items ->
            adapter.submitList(items)
            val checked = items.count { it.isChecked }
            binding.tvEmptyItems.visibility = if (items.isEmpty()) View.VISIBLE else View.GONE
            binding.tvProgress.text = if (items.isEmpty()) "Nenhum item ainda" else "$checked de ${items.size} itens preparados"
            binding.progressBar.max = if (items.isEmpty()) 1 else items.size
            binding.progressBar.progress = checked
        }

        binding.fabAddItem.setOnClickListener { showAddItemDialog() }
    }

    private fun showAddItemDialog() {
        val dialogBinding = DialogAddItemBinding.inflate(layoutInflater)
        val categories = arrayOf("Documentos", "Roupas", "Eletrônicos", "Higiene", "Medicamentos", "Outros")
        dialogBinding.spinnerCategory.adapter = ArrayAdapter(
            this,
            android.R.layout.simple_spinner_item,
            categories
        ).also { it.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item) }

        AlertDialog.Builder(this)
            .setTitle("Adicionar Item")
            .setView(dialogBinding.root)
            .setPositiveButton("Adicionar") { _, _ ->
                val name = dialogBinding.etItemName.text?.toString()?.trim() ?: return@setPositiveButton
                if (name.isNotEmpty()) {
                    viewModel.insertItem(
                        TravelItem(
                            tripId = tripId,
                            name = name,
                            category = dialogBinding.spinnerCategory.selectedItem?.toString() ?: "Outros"
                        )
                    )
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressedDispatcher.onBackPressed()
        return true
    }
}
