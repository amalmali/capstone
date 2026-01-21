import React from "react";

const HistoryTable = ({ records }) => {
  if (!records || records.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "40px", color: "#a0aec0", backgroundColor: "#f8fafc", borderRadius: "12px" }}>
        <div style={{ fontSize: "2rem", marginBottom: "10px" }}>📁</div>
        لا توجد سجلات مخزنة حالياً في قاعدة البيانات.
      </div>
    );
  }

  return (
    <div style={{ overflowX: "auto", marginTop: "15px", borderRadius: "12px", boxShadow: "0 4px 6px rgba(0,0,0,0.05)" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem", backgroundColor: "#fff" }}>
        <thead>
          <tr style={{ backgroundColor: "#f7fafc", borderBottom: "2px solid #edf2f7", textAlign: "right" }}>
            <th style={headerStyle}>التاريخ</th>
            <th style={headerStyle}>المحمية</th>
            <th style={headerStyle}>نوع المخالفة</th>
            <th style={headerStyle}>المساحة (م²)</th>
            <th style={headerStyle}>مستوى الخطر</th>
            <th style={headerStyle}>الغرامة</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id} style={rowStyle}>
              {/* التاريخ */}
              <td style={cellStyle}>
                {new Date(r.date).toLocaleDateString("ar-SA")}
              </td>
              
              {/* المحمية */}
              <td style={{ ...cellStyle, fontWeight: "600" }}>
                {r.protected_area || "غير محدد"}
              </td>

              {/* نوع المخالفة */}
              <td style={{ ...cellStyle, color: "#4a5568", maxWidth: "200px" }}>
                {r.violation_type}
              </td>

              {/* المساحة */}
              <td style={cellStyle}>
                {r.area_m2 ? r.area_m2.toLocaleString() : "0"}
              </td>

              {/* مستوى الخطر مع الألوان */}
              <td style={cellStyle}>
                <span style={{
                  padding: "5px 10px",
                  borderRadius: "20px",
                  fontSize: "0.7rem",
                  fontWeight: "bold",
                  display: "inline-block",
                  backgroundColor: r.risk_level === "High" ? "#fff5f5" : r.risk_level === "Medium" ? "#fefcbf" : "#f0fff4",
                  color: r.risk_level === "High" ? "#e53e3e" : r.risk_level === "Medium" ? "#d69e2e" : "#38a169",
                  border: `1px solid ${r.risk_level === "High" ? "#feb2b2" : r.risk_level === "Medium" ? "#faf089" : "#c6f6d5"}`
                }}>
                  {r.risk_level === "High" ? "عالي" : r.risk_level === "Medium" ? "متوسط" : "منخفض"}
                </span>
              </td>

              {/* الغرامة */}
              <td style={{ ...cellStyle, fontWeight: "bold", color: "#2d3748" }}>
                {r.fine_amount ? `${r.fine_amount.toLocaleString()} ريال` : "-"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// أنماط التنسيق (Styles)
const headerStyle = { padding: "15px 12px", color: "#4a5568", fontWeight: "700" };
const cellStyle = { padding: "12px", borderBottom: "1px solid #edf2f7", verticalAlign: "middle" };
const rowStyle = { transition: "background 0.2s", cursor: "default" };

export default HistoryTable;