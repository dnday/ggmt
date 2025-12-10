"use client";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect, useState } from "react";
import { LayersControl, MapContainer, Marker, Polyline, Popup, ScaleControl, TileLayer, useMap, useMapEvents } from "react-leaflet";

// Fix for default marker icon
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Ship Icon (Boat)
const shipIcon = L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/2942/2942544.png", // Boat icon
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
});

// Waypoint Icon (Red Flag)
const waypointIcon = L.icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/149/149059.png", // Flag icon
    iconSize: [30, 30],
    iconAnchor: [5, 30],
    popupAnchor: [0, -30],
});

function MapUpdater({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center);
  }, [center, map]);
  return null;
}

function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
    useMapEvents({
        click(e) {
            onMapClick(e.latlng.lat, e.latlng.lng);
        },
    });
    return null;
}

export default function Map({ position, waypoints, onAddWaypoint }: { 
    position: [number, number], 
    waypoints: [number, number][],
    onAddWaypoint: (lat: number, lng: number) => void
}) {
  const [trail, setTrail] = useState<[number, number][]>([]);

  useEffect(() => {
    setTrail(prev => [...prev, position]);
  }, [position]);

  return (
    <MapContainer
      center={position}
      zoom={14}
      scrollWheelZoom={true}
      className="h-full w-full rounded-xl z-0"
    >
      <LayersControl position="topright">
        <LayersControl.BaseLayer checked name="Satellite (Esri World Imagery)">
           <TileLayer
            attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          />
        </LayersControl.BaseLayer>

        <LayersControl.BaseLayer name="Ocean / Bathymetry (Esri Ocean)">
          <TileLayer
            attribution='Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}"
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      <ScaleControl position="bottomleft" imperial={false} />
      <MapUpdater center={position} />
      <MapClickHandler onMapClick={onAddWaypoint} />
      
      {/* Ship Trail */}
      <Polyline positions={trail} pathOptions={{ color: 'blue', dashArray: '5, 10', weight: 3 }} />

      {/* Planned Path (Waypoints) */}
      {waypoints.length > 0 && (
          <Polyline positions={[position, ...waypoints]} pathOptions={{ color: 'red', weight: 2, opacity: 0.7 }} />
      )}

      {/* Waypoint Markers */}
      {waypoints.map((wp, idx) => (
          <Marker key={idx} position={wp} icon={waypointIcon}>
              <Popup>Waypoint {idx + 1}</Popup>
          </Marker>
      ))}

      <Marker position={position} icon={shipIcon}>
        <Popup>
          <strong>Vessel 01</strong><br />
          Lat: {position[0].toFixed(5)}<br />
          Lon: {position[1].toFixed(5)}
        </Popup>
      </Marker>
    </MapContainer>
  );
}
