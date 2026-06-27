package com.travellist.app

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.travellist.app.adapter.TripAdapter
import com.travellist.app.data.AppDatabase
import com.travellist.app.data.Trip
import com.travellist.app.databinding.ActivityMainBinding
import com.travellist.app.databinding.DialogAddTripBinding
import com.travellist.app.repository.TravelRepository
import com.travellist.app.viewmodel.TripViewModel
import com.travellist.app.viewmodel.TripViewModelFactory

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var viewModel: TripViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)

        val db = AppDatabase.getDatabase(this)
        val repo = TravelRepository(db.tripDao(), db.travelItemDao())
        viewModel = ViewModelProvider(this, TripViewModelFactory(repo))[TripViewModel::class.java]

        val adapter = TripAdapter(
            onTripClick = { trip ->
                startActivity(
                    Intent(this, TripDetailActivity::class.java).apply {
                        putExtra(TripDetailActivity.EXTRA_TRIP_ID, trip.id)
                        putExtra(TripDetailActivity.EXTRA_TRIP_NAME, trip.name)
                    }
                )
            },
            onTripDelete = { trip ->
                AlertDialog.Builder(this)
                    .setTitle("Excluir viagem")
                    .setMessage("Deseja excluir \"${trip.name}\"?")
                    .setPositiveButton("Excluir") { _, _ -> viewModel.deleteTrip(trip) }
                    .setNegativeButton("Cancelar", null)
                    .show()
            }
        )

        binding.rvTrips.adapter = adapter

        viewModel.allTrips.observe(this) { trips ->
            adapter.submitList(trips)
            binding.tvEmptyState.visibility = if (trips.isEmpty()) View.VISIBLE else View.GONE
        }

        binding.fabAddTrip.setOnClickListener { showAddTripDialog() }
    }

    private fun showAddTripDialog() {
        val dialogBinding = DialogAddTripBinding.inflate(layoutInflater)
        AlertDialog.Builder(this)
            .setTitle("Nova Viagem")
            .setView(dialogBinding.root)
            .setPositiveButton("Criar") { _, _ ->
                val name = dialogBinding.etTripName.text?.toString()?.trim() ?: return@setPositiveButton
                if (name.isNotEmpty()) {
                    viewModel.insertTrip(
                        Trip(
                            name = name,
                            destination = dialogBinding.etDestination.text?.toString()?.trim() ?: "",
                            departureDate = dialogBinding.etDepartureDate.text?.toString()?.trim() ?: ""
                        )
                    )
                }
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }
}
