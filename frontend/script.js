const $ = id => document.getElementById(id);
let chart = null;
let map, userMarker;

// ---------------- LOGIN / LOGOUT ----------------
function login(){
  window.location="/dashboard.html";
}
function logout(){
  window.location="/index.html";
}

// ---------------- MAP ----------------
function initMap(){
  map = L.map('map').setView([20.5937,78.9629],5);
  L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap'}).addTo(map);
  L.Control.geocoder().addTo(map);

  map.locate({setView:true,maxZoom:15});
  map.on("locationfound", e=>{
    if(userMarker) map.removeLayer(userMarker);
    userMarker = L.marker(e.latlng).addTo(map).bindPopup("📌 You are here!").openPopup();
  });

  // Sample EV Stations
  const chargers = [
    {lat:28.6139,lon:77.2090,name:"Delhi Fast Charger",score:85},
    {lat:19.0760,lon:72.8777,name:"Mumbai Public AC",score:78},
    {lat:12.9716,lon:77.5946,name:"Bengaluru EV Point",score:72},
    {lat:22.5726,lon:88.3639,name:"Kolkata Charger",score:65},
    {lat:13.0827,lon:80.2707,name:"Chennai EV Hub",score:60},
  ];
  
  window.topLocations = chargers; // Save for chart

  chargers.forEach(c=>{
    L.marker([c.lat,c.lon]).addTo(map).bindPopup(`⚡ ${c.name}`);
  });

  updateTop5Chart(chargers);
}

// ---------------- PREDICT ----------------
async function predict(){
  const place = $("placeInput").value.trim();
  if(!place) return alert("Enter place name!");

  $("loader").classList.remove("hidden");
  $("predCard").classList.add("hidden");

  const type_encoded = $("typeSelect").value;

  try {
    const res = await fetch("/api/predict",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({place_name:place,type_encoded})
    });
    const data = await res.json();
    $("loader").classList.add("hidden");

    $("locTitle").textContent = data.location_name;
    $("demandScore").textContent = data.predicted_demand_score;
    $("predNote").textContent = data.note;
    $("predCard").classList.remove("hidden");

    map.setView([data.latitude,data.longitude],12);
    L.marker([data.latitude,data.longitude]).addTo(map)
      .bindPopup(`📍 ${data.location_name}`).openPopup();

    // ---------------- update chart with top 5 including this place ----------------
    let top = window.topLocations.slice(); 
    top.push({lat:data.latitude,lon:data.longitude,name:data.location_name,score:data.predicted_demand_score});
    top.sort((a,b)=>b.score-a.score);
    updateTop5Chart(top.slice(0,5));

  } catch(err){
    console.error(err);
    $("loader").classList.add("hidden");
    alert("Prediction failed!");
  }
}

// ---------------- TOP 5 DEMAND CHART ----------------
function updateTop5Chart(locations){
    const top5 = locations.sort((a,b)=>b.score-a.score).slice(0,5);
    const labels = top5.map(loc=>loc.name);
    const scores = top5.map(loc=>loc.score);
    const ctx = $("top5Chart").getContext("2d");
    if(chart) chart.destroy();
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Demand Score',
                data: scores,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {  
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

// ---------------- AI CHAT ----------------
function toggleChat(){ $("chatPanel").classList.toggle("open"); }

async function sendChat(){
  const input = $("chatInput").value.trim();
  if(!input) return;
  appendMsg("user", input);
  $("chatInput").value="";
  setTimeout(()=>appendMsg("bot","⚡ EV Tip: Keep battery between 20% and 80% for long life!"),700);
}

function appendMsg(type,msg){
  const d=document.createElement("div");
  d.className=type;
  d.innerText=msg;
  $("chatLog").appendChild(d);
  $("chatLog").scrollTop=$("chatLog").scrollHeight;
}

// ---------------- INITIALIZE ----------------
window.onload = () => {
  initMap();
};
