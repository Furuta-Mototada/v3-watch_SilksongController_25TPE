package com.example.grid_watch_udp_datacollector

import android.content.Context
import android.os.Bundle
import android.os.VibrationEffect
import android.os.Vibrator
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.grid_watch_udp_datacollector.ui.theme.Grid_Watch_UDP_DataCollectorTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            Grid_Watch_UDP_DataCollectorTheme {
                DataCollectorScreen()
            }
        }
    }
}

@Composable
fun DataCollectorScreen(viewModel: DataCollectorViewModel = viewModel()) {
    val context = LocalContext.current
    val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    
    // Initialize ViewModel with context
    LaunchedEffect(Unit) {
        viewModel.initialize(context)
    }
    
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("Button Data Collector") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // IP Configuration Section
            IpConfigSection(viewModel)
            
            // Connection Status
            Text(
                text = viewModel.connectionStatus.value,
                style = MaterialTheme.typography.bodyMedium,
                color = if (viewModel.connectionStatus.value.startsWith("Connected")) 
                    Color(0xFF4CAF50) else Color(0xFFF44336),
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            // Button Grid
            ButtonGrid(
                viewModel = viewModel,
                onVibrate = { duration ->
                    if (vibrator.hasVibrator()) {
                        vibrator.vibrate(
                            VibrationEffect.createOneShot(duration, VibrationEffect.DEFAULT_AMPLITUDE)
                        )
                    }
                }
            )
            
            Spacer(modifier = Modifier.weight(1f))
            
            // Reset Button
            Button(
                onClick = { viewModel.resetCounts() },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MaterialTheme.colorScheme.error
                )
            ) {
                Text("Reset All Counts")
            }
        }
    }
}

@Composable
fun IpConfigSection(viewModel: DataCollectorViewModel) {
    var ipInput by remember { mutableStateOf(viewModel.serverIP.value) }
    var showDialog by remember { mutableStateOf(false) }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Server IP: ${viewModel.serverIP.value}",
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Bold
            )
            
            Button(
                onClick = { showDialog = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Change IP Address")
            }
        }
    }
    
    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text("Enter Server IP") },
            text = {
                OutlinedTextField(
                    value = ipInput,
                    onValueChange = { ipInput = it },
                    label = { Text("IP Address") },
                    placeholder = { Text("192.168.1.100") }
                )
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.saveIpAddress(ipInput)
                        showDialog = false
                    }
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
fun ButtonGrid(viewModel: DataCollectorViewModel, onVibrate: (Long) -> Unit) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Row 1: WALK, IDLE
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "WALK",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "IDLE",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }
        
        // Row 2: PUNCH, JUMP
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "PUNCH",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "JUMP",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }
        
        // Row 3: TURN_LEFT, TURN_RIGHT
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                action = "TURN_LEFT",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
            ActionButton(
                action = "TURN_RIGHT",
                viewModel = viewModel,
                onVibrate = onVibrate,
                modifier = Modifier.weight(1f)
            )
        }
    }
}

@Composable
fun ActionButton(
    action: String,
    viewModel: DataCollectorViewModel,
    onVibrate: (Long) -> Unit,
    modifier: Modifier = Modifier
) {
    val count = viewModel.actionCounts[action] ?: 0
    val isRecording = viewModel.recordingAction.value == action
    val countColor = viewModel.getCountColor(count)
    
    val backgroundColor = when {
        isRecording -> Color(0xFF4CAF50) // Green when recording
        else -> Color(0xFF757575) // Gray when not recording
    }
    
    Card(
        modifier = modifier
            .aspectRatio(1f)
            .pointerInput(Unit) {
                detectTapGestures(
                    onPress = {
                        // Button pressed
                        viewModel.onButtonPressed(action)
                        onVibrate(50) // Short vibration
                        
                        // Wait for release
                        tryAwaitRelease()
                        
                        // Button released
                        viewModel.onButtonReleased(action)
                        onVibrate(100) // Longer vibration on release
                    }
                )
            },
        elevation = CardDefaults.cardElevation(defaultElevation = if (isRecording) 8.dp else 2.dp),
        colors = CardDefaults.cardColors(containerColor = backgroundColor)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = action.replace("_", " "),
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                color = Color.White,
                textAlign = TextAlign.Center,
                lineHeight = 20.sp
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = "Count: $count",
                fontSize = 14.sp,
                color = countColor,
                fontWeight = FontWeight.Bold
            )
        }
    }
}