"use client";

import { ArrowLeft, Camera, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function CameraPage() {
  const [imageUrl, setImageUrl] = useState("http://localhost:5000/api/video_feed");
  const [timestamp, setTimestamp] = useState(Date.now());

  // Refresh image every 100ms (10 FPS)
  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(Date.now());
    }, 100);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="flex min-h-screen flex-col bg-black text-white p-4 md:p-8 gap-6">
      {/* Header */}
      <header className="flex items-center justify-between pb-6 border-b border-zinc-800">
        <div className="flex items-center gap-4">
          <Link 
            href="/"
            className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition-colors"
          >
            <ArrowLeft className="h-6 w-6 text-zinc-400" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-300 bg-clip-text text-transparent flex items-center gap-3">
              <Camera className="h-8 w-8 text-purple-400" /> Live Camera Feed
            </h1>
            <p className="text-zinc-400 text-sm mt-1">
              Real-time Object Detection View
            </p>
          </div>
        </div>
      </header>

      {/* Camera View */}
      <div className="flex-1 flex items-center justify-center bg-zinc-900/50 rounded-3xl border border-zinc-800 overflow-hidden relative shadow-2xl shadow-purple-900/10">
        {/* Image Feed */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src={`http://localhost:5000/api/video_feed?t=${timestamp}`} 
          alt="Live Feed" 
          className="w-full h-full object-contain max-h-[80vh]"
        />

        {/* Overlay Info */}
        <div className="absolute top-6 left-6 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full border border-zinc-700 flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-bold tracking-wider text-red-400">LIVE</span>
        </div>

        <div className="absolute bottom-6 right-6 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full border border-zinc-700 flex items-center gap-2 text-zinc-400 text-xs">
           <RefreshCw className="h-3 w-3 animate-spin" /> 10 FPS
        </div>
      </div>
    </main>
  );
}
