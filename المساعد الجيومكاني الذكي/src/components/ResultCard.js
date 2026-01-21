import React from "react";

const ResultCard = ({ result }) => {
  // التحقق من وصول النتيجة
  if (!result) return null;

  // استخراج البيانات مع قيم افتراضية
  const riskLevel = result.Risk_Level || "Low";
  const confidence = result.Confidence || 0; // نسبة التأكد من الموديل
  const reasons = result.Reasons || ["تحليل المعايير الجغرافية والبيئية للمخالفة"];

  
  const statusConfig = {
    High: { 
      color: "#e53e3e", 
      label: "خطر مرتفع جداً", 
      bg: "#fff5f5", 
      icon: "⚠️",
      action: "يتطلب إجراءً فورياً وتصعيداً للمدير الميداني." 
    },
    Medium: { 
      color: "#d69e2e", 
      label: "خطر متوسط", 
      bg: "#fefcbf", 
      icon: "🔔",
      action: "يتطلب مراجعة دقيقة وتوثيقاً إضافياً للأضرار."
    },
    Low: { 
      color: "#38a169", 
      label: "منخفض / مستقر", 
      bg: "#f0fff4", 
      icon: "✅",
      action: "مخالفة معيارية؛ يمكن الاكتفاء بالإجراءات الروتينية."
    }
  };

  const currentKey = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1).toLowerCase();
  const current = statusConfig[currentKey] || statusConfig.Low;

  return (
    <div className="result-card" style={{ 
      backgroundColor: current.bg, 
      borderRight: `8px solid ${current.color}`,
      padding: "25px",
      borderRadius: "15px",
      boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)",
      marginTop: "20px",
      direction: "rtl",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* أيقونة الحالة الخلفية للجمالية */}
      <span style={{ position: "absolute", left: "20px", top: "20px", fontSize: "3rem", opacity: 0.1 }}>
        {current.icon}
      </span>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h4 style={{ margin: 0, color: "#4a5568", fontSize: "1rem" }}>تحليل نظام الذكاء الاصطناعي:</h4>
        {confidence > 0 && (
          <span style={{ backgroundColor: "rgba(0,0,0,0.05)", padding: "4px 10px", borderRadius: "10px", fontSize: "0.8rem", fontWeight: "bold" }}>
            نسبة الثقة: {confidence.toFixed(1)}%
          </span>
        )}
      </div>

      <h2 style={{ color: current.color, margin: "0 0 10px 0", display: "flex", alignItems: "center", gap: "10px" }}>
        <span>{current.icon}</span>
        {current.label}
      </h2>
      
      <div style={{ borderTop: `1px solid ${current.color}33`, paddingTop: "15px" }}>
        <p style={{ fontWeight: "bold", color: "#2d3748", fontSize: "0.95rem", marginBottom: "10px" }}>
          التحليل التقديري:
        </p>
        <ul style={{ paddingRight: "20px", margin: "0 0 15px 0" }}>
          {reasons.map((r, i) => (
            <li key={i} style={{ color: "#4a5568", fontSize: "0.9rem", marginBottom: "6px" }}>
              {r}
            </li>
          ))}
        </ul>

        <div style={{ backgroundColor: "white", padding: "10px 15px", borderRadius: "8px", border: `1px dashed ${current.color}` }}>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "#2d3748" }}>
            <strong>💡 التوصية المقترحة:</strong> {current.action}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultCard;