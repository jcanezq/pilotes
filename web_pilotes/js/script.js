document.addEventListener('DOMContentLoaded', () => {
    // --- Tabs Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const resultadosSection = document.getElementById('resultados-section');
    const txtResultados = document.getElementById('txt-resultados');
    let chartInstance = null;

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and corresponding form
            btn.classList.add('active');
            const target = btn.getAttribute('data-target');
            document.getElementById(`form-${target}`).classList.add('active');
            
            // Hide results on tab switch
            resultadosSection.classList.add('hidden');
        });
    });

    // --- Chart Logic ---
    function renderChart(labelQp, dataQp, labelQs, dataQs, titulo) {
        const ctx = document.getElementById('chartResultados').getContext('2d');
        
        if (chartInstance) {
            chartInstance.destroy();
        }

        Chart.defaults.color = '#94A3B8';
        Chart.defaults.font.family = "'Inter', sans-serif";

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Capacidades (kN)'],
                datasets: [
                    {
                        label: labelQp,
                        data: [dataQp],
                        backgroundColor: 'rgba(16, 185, 129, 0.8)', // Emerald
                        borderColor: '#10B981',
                        borderWidth: 1,
                        borderRadius: 8
                    },
                    {
                        label: labelQs,
                        data: [dataQs],
                        backgroundColor: 'rgba(79, 70, 229, 0.8)', // Indigo
                        borderColor: '#4F46E5',
                        borderWidth: 1,
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#F8FAFC' }
                    },
                    title: {
                        display: true,
                        text: titulo,
                        color: '#F8FAFC',
                        font: { size: 16 }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: '#94A3B8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94A3B8' }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    // --- Formulas & Logic ---

    // 1. Arcilla
    document.getElementById('form-arcilla').addEventListener('submit', (e) => {
        e.preventDefault();
        const diametro = parseFloat(document.getElementById('arc-dia').value);
        const longitud = parseFloat(document.getElementById('arc-lon').value);
        const cu = parseFloat(document.getElementById('arc-cu').value);
        const alpha = parseFloat(document.getElementById('arc-alpha').value);

        const area = (Math.PI * Math.pow(diametro, 2)) / 4;
        const perimetro = Math.PI * diametro;

        const Qp = area * cu * 9.0;
        const Qs = perimetro * longitud * (alpha * cu);
        const Qu = Qp + Qs;

        const reporte = `--- Resultados: Cálculo en Arcilla ---\nDiámetro: ${diametro.toFixed(2)} m\nLongitud: ${longitud.toFixed(2)} m\nCohesión (cu): ${cu.toFixed(2)} kN/m²\nAlfa: ${alpha.toFixed(2)}\n------------------------------------\nResistencia de punta (Qp): ${Qp.toFixed(2)} kN\nFricción lateral (Qs):     ${Qs.toFixed(2)} kN\nCapacidad total (Qu):      ${Qu.toFixed(2)} kN`;

        txtResultados.textContent = reporte;
        resultadosSection.classList.remove('hidden');
        resultadosSection.scrollIntoView({ behavior: 'smooth' });

        renderChart('Resistencia de Punta (Qp)', Qp, 'Fricción Lateral (Qs)', Qs, 'Capacidad Última en Arcilla');
    });

    // 2. ENR
    document.getElementById('form-enr').addEventListener('submit', (e) => {
        e.preventDefault();
        const E = parseFloat(document.getElementById('enr-e').value);
        const W_R = parseFloat(document.getElementById('enr-wr').value);
        const h = parseFloat(document.getElementById('enr-h').value);
        const S = parseFloat(document.getElementById('enr-s').value);
        const C = parseFloat(document.getElementById('enr-c').value);
        const n = parseFloat(document.getElementById('enr-n').value);
        const W_p = parseFloat(document.getElementById('enr-wp').value);

        const energia = E * W_R * h;
        const termino_pesos = (W_R + (Math.pow(n, 2)) * W_p) / (W_R + W_p);
        const Qu = (energia / (S + C)) * termino_pesos;

        const reporte = `--- Resultados: Fórmula ENR Modificada ---\nEficiencia: ${E}\nPeso ariete: ${W_R} kN\nAltura caída: ${h} mm\nPenetración: ${S} mm\nConstante C: ${C} mm\nRestitución n: ${n}\nPeso pilote: ${W_p} kN\n------------------------------------------\nCapacidad última (Qu): ${Qu.toFixed(2)} kN`;

        txtResultados.textContent = reporte;
        resultadosSection.classList.remove('hidden');
        resultadosSection.scrollIntoView({ behavior: 'smooth' });

        // Chart with only total capacity for ENR
        renderChart('Capacidad Total (Qu)', Qu, 'No aplica', 0, 'Capacidad Última ENR');
    });

    // 3. SPT
    document.getElementById('form-spt').addEventListener('submit', (e) => {
        e.preventDefault();
        const diametro = parseFloat(document.getElementById('spt-dia').value);
        const longitud = parseFloat(document.getElementById('spt-lon').value);
        const pa = parseFloat(document.getElementById('spt-pa').value);
        const n60 = parseFloat(document.getElementById('spt-n60').value);

        const area = (Math.PI * Math.pow(diametro, 2)) / 4;
        const perimetro = Math.PI * diametro;

        // Qp
        const L_D = longitud / diametro;
        const qp_calculado = 0.4 * pa * n60 * L_D;
        const qp_limite = 4 * pa * n60;
        const qp = Math.min(qp_calculado, qp_limite);
        const Qp = area * qp;

        // Qs (alto desplazamiento)
        const f_prom = 0.02 * pa * n60;
        const Qs = perimetro * longitud * f_prom;
        
        const Qu = Qp + Qs;

        const reporte = `--- Resultados: Cálculo SPT en Arena ---\nDiámetro: ${diametro.toFixed(2)} m\nLongitud: ${longitud.toFixed(2)} m\nN60: ${n60}\npa: ${pa} kN/m²\n----------------------------------------\nResistencia de punta (Qp): ${Qp.toFixed(2)} kN\nFricción lateral (Qs):     ${Qs.toFixed(2)} kN\nCapacidad total (Qu):      ${Qu.toFixed(2)} kN`;

        txtResultados.textContent = reporte;
        resultadosSection.classList.remove('hidden');
        resultadosSection.scrollIntoView({ behavior: 'smooth' });

        renderChart('Resistencia de Punta (Qp)', Qp, 'Fricción Lateral (Qs)', Qs, 'Capacidad Última SPT en Arena');
    });
});
