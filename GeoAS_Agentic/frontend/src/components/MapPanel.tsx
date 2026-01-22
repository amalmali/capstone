import { motion } from "framer-motion";
import { Map, Plus, MapPin } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface MapPanelProps {
  onAddPoint: (lat: number, lng: number) => void;
}

const MapPanel = ({ onAddPoint }: MapPanelProps) => {
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Initialize map
    mapRef.current = L.map(mapContainerRef.current).setView([25.13, 46.57], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapRef.current);

    // Add demo protected zones (for visual demonstration)
    const demoZones = [
      {
        coords: [[26.5, 44], [27, 45], [26, 45.5], [25.5, 44.5]] as L.LatLngTuple[],
        level: "high",
        name: "محمية الإمام تركي",
      },
      {
        coords: [[24, 47], [24.5, 48], [23.5, 48.5], [23, 47.5]] as L.LatLngTuple[],
        level: "medium",
        name: "محمية الأحساء",
      },
    ];

    demoZones.forEach((zone) => {
      const color = zone.level === "high" ? "#ef4444" : zone.level === "medium" ? "#f59e0b" : "#38bdf8";
      L.polygon(zone.coords, {
        color,
        weight: 2,
        fillOpacity: 0.15,
      })
        .bindPopup(`<b>${zone.name}</b><br/>مستوى الحماية: ${zone.level}`)
        .addTo(mapRef.current!);
    });

    // Demo point
    L.circleMarker([24.7, 46.7], {
      radius: 8,
      color: "#22c55e",
      fillColor: "#22c55e",
      fillOpacity: 1,
    })
      .bindPopup("موقع تجريبي داخل المحمية")
      .addTo(mapRef.current);

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  const handleAddPoint = async () => {
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);

    if (!Number.isFinite(latNum) || !Number.isFinite(lngNum)) {
      alert("إحداثيات غير صحيحة");
      return;
    }

    setIsAdding(true);
    
    // Add marker to map
    if (mapRef.current) {
      L.circleMarker([latNum, lngNum], {
        radius: 8,
        color: "#22c55e",
        fillColor: "#22c55e",
        fillOpacity: 1,
      })
        .bindPopup(`Lat: ${latNum}, Lng: ${lngNum}`)
        .addTo(mapRef.current);
      
      mapRef.current.setView([latNum, lngNum], 10);
    }

    onAddPoint(latNum, lngNum);
    setLat("");
    setLng("");
    setIsAdding(false);
  };

  return (
    <motion.div
      className="panel"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 rounded-xl bg-primary/10 border border-primary/20">
          <Map className="w-5 h-5 text-primary" />
        </div>
        <h3 className="section-title mb-0">الخريطة</h3>
      </div>

      <div className="relative">
        {/* Map Controls */}
        <div className="map-controls">
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder="Lat"
              className="input-field w-24 text-sm py-2"
              inputMode="decimal"
            />
            <input
              type="text"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              placeholder="Lng"
              className="input-field w-24 text-sm py-2"
              inputMode="decimal"
            />
          </div>
          <button
            onClick={handleAddPoint}
            disabled={isAdding}
            className="btn-primary-gradient w-full flex items-center justify-center gap-2 py-2 text-sm"
          >
            <Plus className="w-4 h-4" />
            <span>إضافة نقطة</span>
          </button>
        </div>

        {/* Map Container */}
        <div
          ref={mapContainerRef}
          className="map-container h-[500px] md:h-[550px]"
        />
      </div>

      <div className="legend flex flex-wrap gap-4 mt-4">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500" />
          <span>موقعك الحالي</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-success" />
          <span>داخل المحمية</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-destructive" />
          <span>خارج المحمية</span>
        </div>
      </div>

      <p className="hint-text mt-3">
        <MapPin className="w-4 h-4 inline-block ml-1" />
        اضغطي على النقطة لعرض التفاصيل
      </p>
    </motion.div>
  );
};

export default MapPanel;
