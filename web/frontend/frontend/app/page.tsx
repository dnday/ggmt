"use client";

import { Activity, Battery, Gauge, MapPin, Navigation, Trash2 } from "lucide-react";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

// Dynamically import Map to avoid SSR issues
const Map = dynamic(() => import("@/components/Map"), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-zinc-900 text-zinc-500 rounded-xl">
      Loading Map...
    </div>
  ),
});

interface ShipStatus {
  mode: string;
  battery: number;
  speed: number;
  latitude: number;
  longitude: number;
  last_object: string;
}

export default function Home() {
  const [status, setStatus] = useState<ShipStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [waypoints, setWaypoints] = useState<[number, number][]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:5000/api/telemetry");
        const data = await res.json();
        setStatus(data);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching telemetry:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleAddWaypoint = (lat: number, lng: number) => {
      setWaypoints(prev => [...prev, [lat, lng]]);
  };

  const clearWaypoints = () => {
      setWaypoints([]);
  };

  const startMission = async () => {
      // 1. Upload Waypoints
      if (waypoints.length > 0) {
          await fetch('http://localhost:5000/api/waypoints', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ waypoints })
          });
      }

      // 2. Start Command
      await fetch('http://localhost:5000/api/command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: 'START' })
      });
  };

  if (loading || !status) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-black text-white">
        <div className="flex flex-col items-center gap-4">
          <Activity className="h-10 w-10 animate-spin text-blue-500" />
          <p className="text-lg font-medium">Connecting to Ship...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col bg-black text-white p-4 md:p-8 gap-6">
      {/* Header */}
      <header className="flex items-center justify-between pb-6 border-b border-zinc-800">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
            Vessel Monitoring System
          </h1>
          <p className="text-zinc-400 text-sm mt-1">
            Real-time Telemetry & Position
          </p>
        </div>
        <div className="flex items-center gap-3 bg-zinc-900/50 px-4 py-2 rounded-full border border-zinc-800">
          <div
            className={`h-3 w-3 rounded-full ${
              status.mode === "IDLE" ? "bg-yellow-500" : "bg-green-500"
            } animate-pulse`}
          />
          <span className="font-mono font-bold text-sm tracking-wider">
            {status.mode}
          </span>
        </div>
      </header>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
        {/* Map Section (Takes up 3 columns) */}
        <div className="lg:col-span-3 h-[500px] lg:h-auto bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden relative shadow-2xl shadow-blue-900/10">
          <Map 
            position={[status.latitude, status.longitude]} 
            waypoints={waypoints}
            onAddWaypoint={handleAddWaypoint}
          />
          
          {/* Map Overlay Info */}
          <div className="absolute top-4 right-16 bg-black/80 backdrop-blur-md p-4 rounded-xl border border-zinc-700 z-[1000]">
            <div className="flex items-center gap-2 text-zinc-400 text-xs uppercase tracking-wider mb-1">
              <MapPin className="h-3 w-3" /> Coordinates
            </div>
            <div className="font-mono text-lg font-bold text-white">
              {status.latitude.toFixed(6)}, {status.longitude.toFixed(6)}
            </div>
          </div>
          
           {/* Waypoint Info Overlay */}
           <div className="absolute bottom-8 left-20 bg-black/80 backdrop-blur-md p-3 rounded-xl border border-zinc-700 z-[1000] flex items-center gap-4">
            <div className="text-sm">
                <span className="text-zinc-400">Waypoints:</span> <span className="font-bold text-white">{waypoints.length}</span>
            </div>
            {waypoints.length > 0 && (
                <button onClick={clearWaypoints} className="text-red-400 hover:text-red-300 transition-colors">
                    <Trash2 className="h-4 w-4" />
                </button>
            )}
          </div>
        </div>

        {/* Sidebar Stats (Takes up 1 column) */}
        <div className="flex flex-col gap-4">
          {/* Speed Card */}
          <div className="bg-zinc-900/50 backdrop-blur-sm p-6 rounded-2xl border border-zinc-800 hover:border-blue-500/50 transition-colors group">
            <div className="flex items-center justify-between mb-4">
              <span className="text-zinc-400 font-medium">Speed</span>
              <Gauge className="h-6 w-6 text-blue-500 group-hover:scale-110 transition-transform" />
            </div>
            <div className="flex items-end gap-2">
              <span className="text-5xl font-bold font-mono text-white">
                {status.speed}
              </span>
              <span className="text-zinc-500 font-medium mb-2">knots</span>
            </div>
            <div className="w-full bg-zinc-800 h-1.5 mt-4 rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${(status.speed / 10) * 100}%` }}
              />
            </div>
          </div>

          {/* Battery Card */}
          <div className="bg-zinc-900/50 backdrop-blur-sm p-6 rounded-2xl border border-zinc-800 hover:border-green-500/50 transition-colors group">
            <div className="flex items-center justify-between mb-4">
              <span className="text-zinc-400 font-medium">Battery</span>
              <Battery className="h-6 w-6 text-green-500 group-hover:scale-110 transition-transform" />
            </div>
            <div className="flex items-end gap-2">
              <span className="text-5xl font-bold font-mono text-white">
                {Math.round(status.battery)}
              </span>
              <span className="text-zinc-500 font-medium mb-2">%</span>
            </div>
             <div className="w-full bg-zinc-800 h-1.5 mt-4 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${status.battery < 20 ? 'bg-red-500' : 'bg-green-500'}`}
                style={{ width: `${status.battery}%` }}
              />
            </div>
          </div>

          {/* Controls / Actions */}
          <div className="bg-zinc-900/50 backdrop-blur-sm p-6 rounded-2xl border border-zinc-800 flex-1">
            <h3 className="text-zinc-400 font-medium mb-4 flex items-center gap-2">
              <Navigation className="h-4 w-4" /> Mission Control
            </h3>
            <div className="grid grid-cols-1 gap-3">
              <button 
                onClick={startMission}
                className="py-3 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-all active:scale-95"
              >
                Start Mission
              </button>
              <button 
                 onClick={() => fetch('http://localhost:5000/api/command', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ command: 'STOP' })
                })}
                className="py-3 px-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-xl font-medium transition-all active:scale-95"
              >
                Stop / Idle
              </button>
               <button 
                 onClick={() => fetch('http://localhost:5000/api/command', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ command: 'RTH' })
                })}
                className="py-3 px-4 bg-zinc-800 hover:bg-zinc-700 text-orange-400 rounded-xl font-medium transition-all active:scale-95"
              >
                Return to Home
              </button>
            </div>
            <p className="text-xs text-zinc-500 mt-4 text-center">
                Click map to add waypoints
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
