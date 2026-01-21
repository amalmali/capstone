import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LabelList
} from 'recharts';

const RiskChart = ({ data }) => {
  
  const processData = () => {
    const counts = { High: 0, Medium: 0, Low: 0 };
    if (data && data.length > 0) {
      data.forEach(item => {
        
        const level = item.risk_level || item.Risk_Level;
        if (counts[level] !== undefined) counts[level]++;
      });
    }
    return [
      { name: 'منخفض', value: counts.Low, color: '#48bb78', grad: 'colorLow' },
      { name: 'متوسط', value: counts.Medium, color: '#f6ad55', grad: 'colorMed' },
      { name: 'عالي', value: counts.High, color: '#f56565', grad: 'colorHigh' },
    ];
  };

  const chartData = processData();

  return (
    <div style={{ width: '100%', height: 350, backgroundColor: '#fff', padding: '20px', borderRadius: '15px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)' }}>
      <h4 style={{ textAlign: 'right', marginBottom: '20px', color: '#4a5568', fontFamily: 'Arial' }}>إحصائيات مستويات المخاطر</h4>
      
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 10 }}>
          <defs>
            <linearGradient id="colorLow" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#48bb78" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#48bb78" stopOpacity={0.2}/>
            </linearGradient>
            <linearGradient id="colorMed" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f6ad55" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#f6ad55" stopOpacity={0.2}/>
            </linearGradient>
            <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f56565" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#f56565" stopOpacity={0.2}/>
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
          
          <XAxis 
            dataKey="name" 
            axisLine={false} 
            tickLine={false} 
            tick={{ fill: '#718096', fontSize: 13, fontWeight: 'bold' }} 
          />
          
          <YAxis 
            hide={true} 
          />
          
          <Tooltip 
            cursor={{ fill: '#f7fafc', opacity: 0.5 }}
            contentStyle={{ 
              backgroundColor: '#2d3748', 
              borderRadius: '10px', 
              border: 'none', 
              color: '#fff',
              textAlign: 'right',
              direction: 'rtl',
              fontSize: '12px'
            }}
          />

          <Bar dataKey="value" radius={[10, 10, 0, 0]} barSize={50}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={`url(#${entry.grad})`} stroke={entry.color} strokeWidth={1} />
            ))}
            <LabelList 
              dataKey="value" 
              position="top" 
              style={{ fill: '#4a5568', fontWeight: 'bold', fontSize: '14px' }}
              formatter={(val) => (val === 0 ? '' : `${val} حالة`)} 
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskChart;