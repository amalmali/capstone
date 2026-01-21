import React, { useState, useEffect, useCallback } from "react";
import api from "../api/api";
import PredictionForm from "../components/PredictionForm";
import ResultCard from "../components/ResultCard";
import RiskChart from "../components/RiskChart";
import HistoryTable from "../components/HistoryTable";

const Dashboard = ({ setLoggedIn }) => {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get("/history");
      setHistory(response.data);
    } catch (err) {
      console.error("خطأ في جلب السجل التاريخي:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleNewPrediction = (data) => {
    setPredicting(true);
    setResult(data);
    setTimeout(() => {
      fetchDashboardData();
      setPredicting(false);
    }, 800);
  };

  return (
    <div style={containerStyle}>
      {/* الشريط العلوي بالألوان الجديدة */}
      <header style={headerStyle}>
        <div>
          <h2 style={{ color: "#778873", margin: 0, display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "1.5rem" }}>🌿</span> 
            نظام التحليل البيئي الذكي (AI)
          </h2>
          <p style={{ fontSize: "0.85rem", color: "#778873", opacity: 0.8, margin: "5px 0 0 0" }}>
            إدارة المحميات الطبيعية • {new Date().toLocaleDateString('ar-SA')}
          </p>
        </div>
        {predicting && <span style={{ color: "#A1BC98", fontWeight: "bold" }}>جاري التحليل...</span>}
      </header>

      <main style={mainGridStyle}>
        
        {/* القسم الأيمن: الإدخال والنتيجة */}
        <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
          <div style={cardStyle}>
             <PredictionForm setResult={handleNewPrediction} isPredicting={predicting} />
          </div>
          
          {result && (
            <div style={{ animation: "slideUp 0.5s ease-out" }}>
              <ResultCard result={result} />
            </div>
          )}
        </div>

        {/* القسم الأيسر: الإحصائيات والسجل */}
        <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
          
          {/* الرسم البياني */}
          <div style={cardStyle}>
            <h3 style={cardTitleStyle}>📊 توزيع مستويات المخاطر المرصودة</h3>
            <RiskChart data={history} />
          </div>

          {/* جدول السجلات */}
          <div style={{ ...cardStyle, flexGrow: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
              <h3 style={cardTitleStyle}>📜 سجل الرصد والتحليل الأخير</h3>
              {loading && <div className="spinner" style={spinnerStyle}></div>}
            </div>
            <HistoryTable records={history} />
          </div>

        </div>
      </main>
    </div>
  );
};

// --- التنسيقات الموحدة بالألوان المطلوبة ---
const containerStyle = { 
  direction: "rtl", 
  backgroundColor: "#F1F3E0", // اللون الكريمي الأساسي للخلفية
  height: "auto", 
  minHeight: "100vh", 
  width: "100%",
  padding: "20px", 
  fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  display: "block",
  overflowY: "visible" 
};

const headerStyle = { 
  backgroundColor: "#D2DCB6", // الأخضر الفاتح للهيدر
  padding: "20px 30px", 
  borderRadius: "16px", 
  display: "flex", 
  justifyContent: "space-between", 
  alignItems: "center", 
  boxShadow: "0 2px 8px rgba(119, 136, 115, 0.1)", 
  marginBottom: "20px",
  borderRight: "6px solid #778873" // لمسة جمالية بالأخضر الداكن
};

const mainGridStyle = { 
  display: "grid", 
  gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", 
  gap: "25px", 
  maxWidth: "100%",
  paddingBottom: "40px" 
};

const cardStyle = { 
  backgroundColor: "#ffffff", // الحفاظ على خلفية الكروت بيضاء لسهولة القراءة
  padding: "25px", 
  borderRadius: "16px", 
  boxShadow: "0 4px 15px rgba(119, 136, 115, 0.08)",
  border: "1px solid #D2DCB6", // حدود بلون الأخضر الفاتح
  height: "fit-content" 
};

const cardTitleStyle = { 
  marginTop: 0, 
  color: "#778873", // النص باللون الأخضر الداكن
  fontSize: "1.1rem", 
  fontWeight: "700", 
  borderRight: "4px solid #A1BC98", // التمييز باللون المتوسط
  paddingRight: "10px" 
};

const spinnerStyle = { 
  width: "20px", 
  height: "20px", 
  border: "3px solid #F1F3E0", 
  borderTop: "3px solid #778873", 
  borderRadius: "50%", 
  animation: "spin 1s linear infinite" 
};

export default Dashboard;