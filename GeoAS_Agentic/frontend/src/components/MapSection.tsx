import { useState, useEffect, useRef, useCallback } from "react";
import { Plus, Layers, MapPin, Check, Navigation } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getMapData } from "@/services/api";

interface ReserveInfo {
  name: string;
  protectionLevel: "high" | "medium" | "low";
  isInside: boolean;
}

interface MapSectionProps {
  onAddPoint: (lat: number, lng: number) => void;
  reserveInfo: ReserveInfo | null;
}

interface RippleEffect {
  id: number;
  x: number;
  y: number;
}

const MapSection = ({ onAddPoint, reserveInfo }: MapSectionProps) => {
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [ripples, setRipples] = useState<RippleEffect[]>([]);
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [lastAddedCoords, setLastAddedCoords] = useState<{ lat: number; lng: number } | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const zonesLayerRef = useRef<L.GeoJSON | null>(null);
  const pointsLayerRef = useRef<L.GeoJSON | null>(null);
  const userMarkerRef = useRef<L.CircleMarker | null>(null);
  const addedMarkersRef = useRef<L.CircleMarker[]>([]);

  // Load map data from API
  const loadMapData = useCallback(async () => {
    if (!mapRef.current) return;
    
    try {
      const data = await getMapData();
      
      // Clear existing layers
      if (zonesLayerRef.current) {
        zonesLayerRef.current.clearLayers();
      }
      if (pointsLayerRef.current) {
        pointsLayerRef.current.clearLayers();
      }
      
      // Add zones
      if (data.zones && zonesLayerRef.current) {
        zonesLayerRef.current.addData(data.zones);
      }
      
      // Add points
      if (data.points && pointsLayerRef.current) {
        pointsLayerRef.current.addData(data.points);
      }
    } catch (error) {
      console.error("Failed to load map data:", error);
    }
  }, []);

  // Get user's current location from device GPS
  const getUserLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError("المتصفح لا يدعم تحديد الموقع");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });
        setLocationError(null);
        
        // Update user marker on map
        if (mapRef.current) {
          if (userMarkerRef.current) {
            userMarkerRef.current.setLatLng([latitude, longitude]);
          } else {
            userMarkerRef.current = L.circleMarker([latitude, longitude], {
              radius: 10,
              color: "#1e3a5f",
              fillColor: "#1e3a5f",
              fillOpacity: 1,
              weight: 3,
            })
              .bindPopup("📍 موقعك الحالي")
              .addTo(mapRef.current);
          }
          
          // Fly to user location
          mapRef.current.flyTo([latitude, longitude], 12, {
            duration: 1.5,
          });
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError("تم رفض إذن تحديد الموقع");
            break;
          case error.POSITION_UNAVAILABLE:
            setLocationError("الموقع غير متاح");
            break;
          case error.TIMEOUT:
            setLocationError("انتهت مهلة تحديد الموقع");
            break;
          default:
            setLocationError("خطأ في تحديد الموقع");
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000,
      }
    );
  }, []);

  // Watch user location continuously
  useEffect(() => {
    if (!navigator.geolocation) return;

    const watchId = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lng: longitude });
        
        // Update user marker position
        if (mapRef.current && userMarkerRef.current) {
          userMarkerRef.current.setLatLng([latitude, longitude]);
        }
      },
      (error) => {
        console.error("Watch position error:", error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 30000,
      }
    );

    return () => {
      navigator.geolocation.clearWatch(watchId);
    };
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Initialize map centered on Saudi Arabia
    mapRef.current = L.map(mapContainerRef.current).setView([25.13, 46.57], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapRef.current);

    // Initialize zones layer (polygons)
    zonesLayerRef.current = L.geoJSON(undefined, {
      style: (feature) => {
        const level = feature?.properties?.protection_level;
        return {
          color: level === "high" ? "#dc2626" : level === "medium" ? "#d97706" : "#0ea5e9",
          weight: 2,
          fillOpacity: 0.15
        };
      }
    }).addTo(mapRef.current);

    // Initialize points layer
    pointsLayerRef.current = L.geoJSON(undefined, {
      pointToLayer: (feature, latlng) => {
        const visual = feature.properties?.visual || {};
        const color = visual.color || "#ef4444";
        const radius = visual.radius || 6;
        const popup = visual.popup || "";
        return L.circleMarker(latlng, {
          radius,
          color,
          fillColor: color,
          fillOpacity: 1
        }).bindPopup(popup);
      }
    }).addTo(mapRef.current);

    // Load initial map data from backend
    loadMapData();

    // Get user's GPS location
    getUserLocation();

    // Refresh map data every 5 seconds
    const interval = setInterval(loadMapData, 5000);

    return () => {
      clearInterval(interval);
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [loadMapData, getUserLocation]);

  const handleAddPoint = async () => {
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);

    if (!Number.isFinite(latNum) || !Number.isFinite(lngNum)) {
      alert("إحداثيات غير صحيحة");
      return;
    }

    setIsAdding(true);
    
    if (mapRef.current) {
      // Get screen position for ripple effect
      const point = mapRef.current.latLngToContainerPoint([latNum, lngNum]);
      
      // Add ripple effect
      const rippleId = Date.now();
      setRipples(prev => [...prev, { id: rippleId, x: point.x, y: point.y }]);
      
      // Remove ripple after animation
      setTimeout(() => {
        setRipples(prev => prev.filter(r => r.id !== rippleId));
      }, 1500);

      // Animate to location first
      mapRef.current.flyTo([latNum, lngNum], 10, {
        duration: 1.5,
        easeLinearity: 0.25,
      });
    }

    // Save the coordinates before clearing
    setLastAddedCoords({ lat: latNum, lng: lngNum });

    // Call API to add point and check if inside zone
    await onAddPoint(latNum, lngNum);

    // Show success message
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 2000);

    setLat("");
    setLng("");
    
    setTimeout(() => setIsAdding(false), 1500);
  };

  // Add marker after reserveInfo is updated (after API response)
  useEffect(() => {
    if (!mapRef.current || !reserveInfo || !lastAddedCoords) return;
    
    // Only add marker if we have valid recent coordinates from the success state
    if (showSuccess && mapRef.current) {
      // Determine color based on inside/outside
      const markerColor = reserveInfo.isInside ? "#22c55e" : "#ef4444"; // green or red
      
      // Add the colored marker at the actual coordinates
      const newMarker = L.circleMarker([lastAddedCoords.lat, lastAddedCoords.lng], {
        radius: 8,
        color: markerColor,
        fillColor: markerColor,
        fillOpacity: 1,
        weight: 2,
      })
        .bindPopup(`${reserveInfo.isInside ? "✅ داخل المحمية" : "❌ خارج المحمية"}<br>${reserveInfo.name}`)
        .addTo(mapRef.current);
      
      addedMarkersRef.current.push(newMarker);
      
      // Animate marker
      let radius = 0;
      const animateMarker = setInterval(() => {
        radius += 1;
        newMarker.setRadius(radius);
        if (radius >= 8) {
          clearInterval(animateMarker);
        }
      }, 30);
    }
  }, [reserveInfo, showSuccess, lastAddedCoords]);

  return (
    <section className="map-section relative overflow-hidden">
      {/* Map */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Ripple Effects */}
      <AnimatePresence>
        {ripples.map((ripple) => (
          <motion.div
            key={ripple.id}
            className="absolute pointer-events-none z-[1000]"
            style={{ left: ripple.x, top: ripple.y }}
            initial={{ scale: 0, opacity: 1 }}
            animate={{ scale: 4, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          >
            <div className="w-16 h-16 -ml-8 -mt-8 rounded-full border-4 border-primary" />
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Success Toast */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.9 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className="absolute top-4 left-1/2 -translate-x-1/2 z-[1001] bg-success text-success-foreground px-4 py-2 rounded-lg shadow-lg flex items-center gap-2"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1, type: "spring", stiffness: 400 }}
            >
              <Check className="w-5 h-5" />
            </motion.div>
            <span className="font-semibold text-sm">تمت إضافة النقطة بنجاح</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Overlay - Add Point Controls */}
      <motion.div 
        className="map-overlay map-overlay-top"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center gap-2 mb-3">
          <motion.div 
            className="w-7 h-7 rounded-md bg-primary/10 flex items-center justify-center"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <MapPin className="w-4 h-4 text-primary" />
          </motion.div>
          <span className="text-sm font-semibold text-foreground">إضافة نقطة</span>
        </div>
        <div className="flex gap-2 mb-2">
          <div className="flex-1">
            <input
              type="text"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder="28.3687206555"
              className="input-modern w-full text-xs py-2 px-3"
              inputMode="decimal"
            />
            <span className="text-[10px] text-muted-foreground mt-1 block">Lat</span>
          </div>
          <div className="flex-1">
            <input
              type="text"
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              placeholder="42.87964453"
              className="input-modern w-full text-xs py-2 px-3"
              inputMode="decimal"
            />
            <span className="text-[10px] text-muted-foreground mt-1 block">Lng</span>
          </div>
        </div>
        <motion.button
          onClick={handleAddPoint}
          disabled={isAdding}
          className="btn-primary w-full py-2 text-xs"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <AnimatePresence mode="wait">
            {isAdding ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0, rotate: 0 }}
                animate={{ opacity: 1, rotate: 360 }}
                exit={{ opacity: 0 }}
                transition={{ rotate: { duration: 1, repeat: Infinity, ease: "linear" } }}
                className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full"
              />
            ) : (
              <motion.div
                key="icon"
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0 }}
                className="flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>إضافة</span>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Get My Location Button */}
        <motion.button
          onClick={getUserLocation}
          className="btn-secondary w-full py-2 text-xs mt-2 flex items-center justify-center gap-1"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Navigation className="w-3.5 h-3.5" />
          <span>موقعي الحالي</span>
        </motion.button>

        {/* Location Error Message */}
        {locationError && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-destructive mt-2 text-center"
          >
            {locationError}
          </motion.p>
        )}

        {/* Show current location if available */}
        {userLocation && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-muted-foreground mt-2 text-center bg-muted/50 rounded px-2 py-1"
          >
            📍 {userLocation.lat.toFixed(5)}, {userLocation.lng.toFixed(5)}
          </motion.div>
        )}
      </motion.div>

      {/* Overlay - Legend */}
      <motion.div 
        className="map-overlay absolute z-[1000] bg-card/95 backdrop-blur-sm rounded-lg border p-3"
        style={{ bottom: reserveInfo ? '5rem' : '1rem', right: '1rem' }}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0, bottom: reserveInfo ? '5rem' : '1rem' }}
        transition={{ delay: 0.4 }}
      >
        <div className="flex items-center gap-2 mb-2">
          <Layers className="w-4 h-4 text-muted-foreground" />
          <span className="text-xs font-semibold text-foreground">دليل الألوان</span>
        </div>
        <div className="space-y-1.5">
          <div className="legend-item">
            <motion.span 
              className="legend-dot" 
              style={{ backgroundColor: "#1e3a5f" }}
              whileHover={{ scale: 1.3 }}
            />
            <span>موقعك</span>
          </div>
          <div className="legend-item">
            <motion.span 
              className="legend-dot bg-success"
              whileHover={{ scale: 1.3 }}
            />
            <span>داخل المحمية</span>
          </div>
          <div className="legend-item">
            <motion.span 
              className="legend-dot bg-destructive"
              whileHover={{ scale: 1.3 }}
            />
            <span>خارج المحمية</span>
          </div>
        </div>
      </motion.div>

      {/* Zone Info Banner at Bottom */}
      <AnimatePresence>
        {reserveInfo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 25 }}
            className={`absolute bottom-4 left-4 right-4 z-[1000] rounded-lg px-4 py-3 backdrop-blur-sm flex items-center justify-between ${
              reserveInfo.isInside 
                ? "bg-success/90 text-success-foreground" 
                : "bg-destructive/90 text-destructive-foreground"
            }`}
          >
            <div className="flex items-center gap-3">
              <MapPin className="w-5 h-5" />
              <div>
                <p className="font-bold text-sm">{reserveInfo.name}</p>
                <p className="text-xs opacity-90">
                  {reserveInfo.isInside ? "داخل المحمية" : "خارج المحمية"}
                </p>
              </div>
            </div>
            {reserveInfo.isInside && (
              <div className="flex items-center gap-2 bg-white/20 rounded-full px-3 py-1">
                <span className="text-xs font-semibold">
                  مستوى الحماية: {
                    reserveInfo.protectionLevel === "high" ? "عالي" :
                    reserveInfo.protectionLevel === "medium" ? "متوسط" : "منخفض"
                  }
                </span>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

export default MapSection;