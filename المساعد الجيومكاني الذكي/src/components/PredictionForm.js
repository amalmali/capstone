import React, { useState } from "react";
import api from "../api/api";

const PredictionForm = ({ setResult }) => {
  const [formData, setFormData] = useState({
    Protected_Area: "روضة التنهات",
    Violation_Type: "قطع الأشجار أو الاحتطاب", 
    Season: "Summer",
    Area_m2: "", 
    Distance_To_Road_km: "", 
    Distance_To_Urban_km: "", 
    Year: 2026,
    Fine_Amount: "" 
  });

  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let finalValue = type === "number" ? (value === "" ? "" : parseFloat(value)) : value;
    
    setFormData(prev => ({
      ...prev,
      [name]: finalValue
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/predict", formData);
      setResult(response.data);
    } catch (error) {
      console.error("Error:", error);
      alert("حدث خطأ أثناء التحليل، يرجى التأكد من تشغيل السيرفر.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h3 style={{ textAlign: "center", color: "#2d3748", marginBottom: "20px" }}>
        نظام تحليل المخاطر البيئية - إدخال بيانات المخالفة
      </h3>
      
      <div style={gridStyle}>
        
        {/* المحمية */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>المحمية</label>
          <select name="Protected_Area" value={formData.Protected_Area} onChange={handleChange} style={selectStyle}>
            <option value="روضة التنهات">روضة التنهات</option>
            <option value="الملك خالد">الملك خالد</option>
            <option value="الإمام تركي">الإمام تركي</option>
            <option value="الملك عبدالعزيز">الملك عبدالعزيز</option>
          </select>
        </div>

        {/* نوع المخالفة - القائمة الكاملة */}
        <div style={{ ...inputGroupStyle, gridColumn: "span 2" }}>
          <label style={labelStyle}>نوع المخالفة (حسب اللائحة التنفيذية)</label>
          <select name="Violation_Type" value={formData.Violation_Type} onChange={handleChange} style={selectStyle}>
            <optgroup label="مخالفات الغطاء النباتي">
              <option value="قطع الأشجار أو الاحتطاب">قطع الأشجار أو الاحتطاب</option>
              <option value="حرق النباتات أو الأشجار">حرق النباتات أو الأشجار</option>
              <option value="إشعال النار في غير الأماكن المخصصة">إشعال النار في غير الأماكن المخصصة</option>
              <option value="الزراعة داخل المحمية بدون ترخيص">الزراعة داخل المحمية بدون ترخيص</option>
            </optgroup>

            <optgroup label="مخالفات الكائنات الفطرية">
              <option value="جمع منتجات كائنات مهددة بالانقراض">جمع منتجات كائنات مهددة بالانقراض</option>
              <option value="إطلاق كائنات فطرية غازية أو دخيلة">إطلاق كائنات فطرية غازية أو دخيلة</option>
            </optgroup>

            <optgroup label="مخالفات الرعي">
              <option value="رعي الإبل أو الأبقار (للرأس الواحد)">رعي الإبل أو الأبقار (للرأس الواحد)</option>
              <option value="رعي الضأن أو الماعز (للرأس الواحد)">رعي الضأن أو الماعز (للرأس الواحد)</option>
              <option value="رعي الماشية الجائر">رعي الماشية الجائر (مساحات واسعة)</option>
            </optgroup>

            <optgroup label="مخالفات الدخول والأنشطة">
              <option value="دخول المحمية بدون تصريح">دخول المحمية بدون تصريح</option>
              <option value="سير المركبات في غير المسارات المخصصة">سير المركبات في غير المسارات المخصصة</option>
              <option value="التخييم في المحمية بدون ترخيص">التخييم في المحمية بدون ترخيص</option>
              <option value="ممارسة أنشطة علمية بدون ترخيص">ممارسة أنشطة علمية بدون ترخيص</option>
            </optgroup>

            <optgroup label="مخالفات الإنشاءات والتخريب">
              <option value="إقامة منشآت أو مبانٍ بدون ترخيص">إقامة منشآت أو مبانٍ بدون ترخيص</option>
              <option value="إتلاف المنشآت الثابتة أو المسيجات">إتلاف المنشآت الثابتة أو المسيجات</option>
            </optgroup>

            <optgroup label="مخالفات التلوث والنفايات">
              <option value="التخلص من نفايات خطرة داخل المحمية">التخلص من نفايات خطرة داخل المحمية</option>
              <option value="ترك أو رمي النفايات غير الخطرة">ترك أو رمي النفايات غير الخطرة</option>
              <option value="رمي نفايات">رمي نفايات (عامة)</option>
            </optgroup>
          </select>
        </div>

        {/* المساحة */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>المساحة المتضررة (م²)</label>
          <input type="number" name="Area_m2" placeholder="0" value={formData.Area_m2} onChange={handleChange} style={inputStyle} required />
        </div>

        {/* السنة */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>السنة</label>
          <input type="number" name="Year" value={formData.Year} onChange={handleChange} style={inputStyle} required />
        </div>

        {/* المسافة عن الطريق */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>البعد عن الطريق (كم)</label>
          <input type="number" step="0.1" name="Distance_To_Road_km" placeholder="مثال: 2.5" value={formData.Distance_To_Road_km} onChange={handleChange} style={inputStyle} required />
        </div>

        {/* المسافة عن العمران */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>البعد عن العمران (كم)</label>
          <input type="number" step="0.1" name="Distance_To_Urban_km" placeholder="مثال: 10.0" value={formData.Distance_To_Urban_km} onChange={handleChange} style={inputStyle} required />
        </div>

        {/* الغرامة */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>قيمة الغرامة (ريال)</label>
          <input type="number" name="Fine_Amount" placeholder="0" value={formData.Fine_Amount} onChange={handleChange} style={inputStyle} required />
        </div>

        {/* الموسم */}
        <div style={inputGroupStyle}>
          <label style={labelStyle}>الموسم</label>
          <select name="Season" value={formData.Season} onChange={handleChange} style={selectStyle}>
            <option value="Winter">الشتاء</option>
            <option value="Spring">الربيع</option>
            <option value="Summer">الصيف</option>
            <option value="Autumn">الخريف</option>
          </select>
        </div>

      </div>

      <button type="submit" disabled={loading} style={loading ? {...buttonStyle, opacity: 0.7} : buttonStyle}>
        {loading ? "جاري المعالجة..." : "بدء تحليل المخاطر"}
      </button>
    </form>
  );
};

// التنسيقات
const formStyle = { direction: "rtl", backgroundColor: "#fff", padding: "30px", borderRadius: "15px", boxShadow: "0 8px 30px rgba(0,0,0,0.08)", maxWidth: "800px", margin: "auto" };
const gridStyle = { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" };
const inputGroupStyle = { display: "flex", flexDirection: "column" };
const labelStyle = { marginBottom: "8px", fontWeight: "600", color: "#4a5568", fontSize: "14px" };
const inputStyle = { padding: "12px", borderRadius: "8px", border: "1px solid #e2e8f0", fontSize: "15px", outline: "none", transition: "border 0.2s" };
const selectStyle = { ...inputStyle, cursor: "pointer", backgroundColor: "#f8fafc" };
const buttonStyle = { gridColumn: "span 2", marginTop: "20px", padding: "16px", backgroundColor: "#2f855a", color: "white", border: "none", borderRadius: "10px", fontSize: "17px", fontWeight: "bold", cursor: "pointer", boxShadow: "0 4px 12px rgba(47, 133, 90, 0.2)" };

export default PredictionForm;