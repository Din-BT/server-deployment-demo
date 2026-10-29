/**
 * NT106 - LẬP TRÌNH MẠNG CĂN BẢN (UIT)
 * Mã nguồn JavaScript điều khiển Demo Client & Đo lường hiệu năng
 * Thành viên phụ trách: TV3 (Client & Đo lường)
 * 
 * Chức năng chính:
 * 1. Gọi trực tiếp tới BaaS Supabase REST API (Kịch bản Phút 2)
 * 2. Gọi trực tiếp tới Self-Hosted Web API .NET 10 (Kịch bản Phút 3)
 * 3. Chạy test tải đối sánh tự động 50-100 requests đo RTT, Min, Avg, P95, Max (Nhiệm vụ Ngày 3)
 * 4. Xuất dữ liệu đo đạc ra file CSV phục vụ làm slide báo cáo
 */

// =========================================================================================
// 1. QUẢN LÝ CẤU HÌNH & TRẠNG THÁI (LOCAL STORAGE)
// =========================================================================================
const STORAGE_KEYS = {
    SELF_HOSTED_URL: 'nt106_self_hosted_url',
    SUPABASE_URL: 'nt106_supabase_url',
    SUPABASE_KEY: 'nt106_supabase_key'
};
  
// Khởi tạo các phần tử DOM
const dom = {
    selfHostedUrl: document.getElementById('selfHostedUrl'),
    supabaseUrl: document.getElementById('supabaseUrl'),
    supabaseKey: document.getElementById('supabaseKey'),
    btnSaveConfig: document.getElementById('btnSaveConfig'),
    clientStatus: document.getElementById('clientStatus'),

    // Demo inputs & buttons
    msgSupabase: document.getElementById('msgSupabase'),
    btnSendSupabase: document.getElementById('btnSendSupabase'),
    statusSupabase: document.getElementById('statusSupabase'),
    rttSupabase: document.getElementById('rttSupabase'),
    sizeSupabase: document.getElementById('sizeSupabase'),

    msgSelfHosted: document.getElementById('msgSelfHosted'),
    btnSendSelfHosted: document.getElementById('btnSendSelfHosted'),
    btnPingSelfHosted: document.getElementById('btnPingSelfHosted'),
    btnMetricsSelfHosted: document.getElementById('btnMetricsSelfHosted'),
    statusSelfHosted: document.getElementById('statusSelfHosted'),
    rttSelfHosted: document.getElementById('rttSelfHosted'),
    sizeSelfHosted: document.getElementById('sizeSelfHosted'),

    // Benchmark DOM
    benchmarkCount: document.getElementById('benchmarkCount'),
    btnRunBenchmark: document.getElementById('btnRunBenchmark'),
    progressContainer: document.getElementById('benchmarkProgressContainer'),
    progressBar: document.getElementById('benchmarkProgressBar'),
    progressText: document.getElementById('benchmarkProgressText'),
    btnExportCsv: document.getElementById('btnExportCsv'),

    // Bảng kết quả benchmark
    bmSupabaseMin: document.getElementById('bmSupabaseMin'),
    bmSupabaseAvg: document.getElementById('bmSupabaseAvg'),
    bmSupabaseP95: document.getElementById('bmSupabaseP95'),
    bmSupabaseMax: document.getElementById('bmSupabaseMax'),
    bmSupabaseSuccess: document.getElementById('bmSupabaseSuccess'),

    bmSelfMin: document.getElementById('bmSelfMin'),
    bmSelfAvg: document.getElementById('bmSelfAvg'),
    bmSelfP95: document.getElementById('bmSelfP95'),
    bmSelfMax: document.getElementById('bmSelfMax'),
    bmSelfMemory: document.getElementById('bmSelfMemory'),
    bmSelfSuccess: document.getElementById('bmSelfSuccess'),

    // Console
    consoleWindow: document.getElementById('consoleWindow'),
    btnClearConsole: document.getElementById('btnClearConsole')
};

// Biến lưu trữ kết quả benchmark gần nhất để xuất CSV
let latestBenchmarkData = [];

// Tải cấu hình đã lưu trước đó (nếu có)
function loadSavedConfig() {
    const savedSelf = localStorage.getItem(STORAGE_KEYS.SELF_HOSTED_URL);
    const savedSupaUrl = localStorage.getItem(STORAGE_KEYS.SUPABASE_URL);
    const savedSupaKey = localStorage.getItem(STORAGE_KEYS.SUPABASE_KEY);

    if (savedSelf) dom.selfHostedUrl.value = savedSelf;
    if (savedSupaUrl) dom.supabaseUrl.value = savedSupaUrl;
    if (savedSupaKey) dom.supabaseKey.value = savedSupaKey;
}

// Lưu cấu hình vào localStorage
dom.btnSaveConfig.addEventListener('click', () => {
    localStorage.setItem(STORAGE_KEYS.SELF_HOSTED_URL, dom.selfHostedUrl.value.trim());
    localStorage.setItem(STORAGE_KEYS.SUPABASE_URL, dom.supabaseUrl.value.trim());
    localStorage.setItem(STORAGE_KEYS.SUPABASE_KEY, dom.supabaseKey.value.trim());
    logToConsole('Đã lưu cấu hình endpoint vào trình duyệt.', 'info');
    alert('✅ Đã lưu cấu hình thành công!');
});

// =========================================================================================
// 2. TIỆN ÍCH GHI LOG RA MÀN HÌNH CONSOLE (NETWORK MONITOR)
// =========================================================================================
function logToConsole(message, type = 'info') {
    const now = new Date();
    const timeStr = `[${now.toTimeString().split(' ')[0]}.${now.getMilliseconds().toString().padStart(3, '0')}]`;
    
    const entry = document.createElement('div');
    entry.className = `console-entry ${type}`;
    entry.innerHTML = `<span class="timestamp">${timeStr}</span> ${message}`;
    
    dom.consoleWindow.appendChild(entry);
    dom.consoleWindow.scrollTop = dom.consoleWindow.scrollHeight;
}

dom.btnClearConsole.addEventListener('click', () => {
    dom.consoleWindow.innerHTML = '';
    logToConsole('Màn hình console đã được xóa.', 'info');
});

// Tính toán phân vị (Percentile) phục vụ tính P95
function calculatePercentile(arr, p) {
    if (arr.length === 0) return 0;
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.min(sorted.length - 1, Math.round((p / 100) * (sorted.length - 1)));
    return sorted[index];
}

// =========================================================================================
// 3. KỊCH BẢN DEMO PHÚT 2: GỬI DỮ LIỆU ĐẾN BAAS SUPABASE
// =========================================================================================
async function sendToSupabase(messageText, isBenchmark = false) {
    const baseUrl = dom.supabaseUrl.value.trim().replace(/\/+$/, '');
    const apiKey = dom.supabaseKey.value.trim();

    if (!baseUrl || !apiKey) {
        if (!isBenchmark) {
            alert('⚠️ Vui lòng nhập Supabase Project URL và Anon Key trong phần Cấu Hình!');
        }
        throw new Error('Thiếu cấu hình Supabase URL hoặc Anon Key');
    }

    const endpoint = `${baseUrl}/rest/v1/network_logs`;
    const payload = {
        sent_at: new Date().toISOString(),
        client_id: 'client-web-demo',
        message: messageText,
        payload_size: new Blob([messageText]).size
    };
    const bodyStr = JSON.stringify(payload);
    const payloadBytes = new Blob([bodyStr]).size;

    const tStart = performance.now();
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'apikey': apiKey,
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            body: bodyStr
        });
        const tEnd = performance.now();
        const rtt = Math.round(tEnd - tStart);

        if (!isBenchmark) {
            dom.statusSupabase.innerText = `${response.status} ${response.statusText || 'Created'}`;
            dom.statusSupabase.style.color = response.ok ? '#34d399' : '#f87171';
            dom.rttSupabase.innerText = `${rtt} ms`;
            dom.sizeSupabase.innerText = `${payloadBytes} bytes (body)`;
            logToConsole(`[SUPABASE] POST /rest/v1/network_logs => Status: ${response.status} | RTT: ${rtt}ms | Payload: ${payloadBytes}B`, 'supabase');
        }

        return { success: response.ok, rtt, status: response.status, bytes: payloadBytes };
    } catch (err) {
        const tEnd = performance.now();
        const rtt = Math.round(tEnd - tStart);
        if (!isBenchmark) {
            dom.statusSupabase.innerText = 'Lỗi kết nối';
            dom.statusSupabase.style.color = '#f87171';
            dom.rttSupabase.innerText = `${rtt} ms`;
            logToConsole(`[SUPABASE ERROR] ${err.message}`, 'error');
        }
        return { success: false, rtt, error: err.message };
    }
}

dom.btnSendSupabase.addEventListener('click', async () => {
    const msg = dom.msgSupabase.value.trim() || 'NT106 Demo Message to Supabase';
    dom.btnSendSupabase.disabled = true;
    try {
        await sendToSupabase(msg);
    } finally {
        dom.btnSendSupabase.disabled = false;
    }
});

// =========================================================================================
// 4. KỊCH BẢN DEMO PHÚT 3: GỬI DỮ LIỆU ĐẾN SELF-HOSTED SERVER (.NET 10)
// =========================================================================================
async function sendToSelfHosted(messageText, isBenchmark = false) {
    const baseUrl = dom.selfHostedUrl.value.trim().replace(/\/+$/, '');
    if (!baseUrl) {
        if (!isBenchmark) alert('⚠️ Vui lòng nhập URL của Self-Hosted Server!');
        throw new Error('Thiếu URL của Self-Hosted Server');
    }

    const endpoint = `${baseUrl}/api/logs`;
    const payload = {
        deviceId: 'Client-Web-NT106',
        level: 'INFO',
        message: messageText,
        metadata: {
            source: 'Browser-Fetch-API',
            clientTime: new Date().toISOString()
        }
    };
    const bodyStr = JSON.stringify(payload);
    const payloadBytes = new Blob([bodyStr]).size;

    const tStart = performance.now();
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: bodyStr
        });
        const tEnd = performance.now();
        const rtt = Math.round(tEnd - tStart);

        if (!isBenchmark) {
            dom.statusSelfHosted.innerText = `${response.status} ${response.statusText || 'OK'}`;
            dom.statusSelfHosted.style.color = response.ok ? '#60a5fa' : '#f87171';
            dom.rttSelfHosted.innerText = `${rtt} ms`;
            dom.sizeSelfHosted.innerText = `${payloadBytes} bytes (body)`;
            logToConsole(`[SELF-HOSTED] POST /api/logs => Status: ${response.status} | RTT: ${rtt}ms | Payload: ${payloadBytes}B`, 'selfhosted');
        }

        return { success: response.ok, rtt, status: response.status, bytes: payloadBytes };
    } catch (err) {
        const tEnd = performance.now();
        const rtt = Math.round(tEnd - tStart);
        if (!isBenchmark) {
            dom.statusSelfHosted.innerText = 'Lỗi kết nối';
            dom.statusSelfHosted.style.color = '#f87171';
            dom.rttSelfHosted.innerText = `${rtt} ms`;
            logToConsole(`[SELF-HOSTED ERROR] ${err.message}. Kiểm tra server đã bật chưa (http://localhost:5000).`, 'error');
        }
        return { success: false, rtt, error: err.message };
    }
}

dom.btnSendSelfHosted.addEventListener('click', async () => {
    const msg = dom.msgSelfHosted.value.trim() || 'NT106 Demo Message to Self-Hosted';
    dom.btnSendSelfHosted.disabled = true;
    try {
        await sendToSelfHosted(msg);
    } finally {
        dom.btnSendSelfHosted.disabled = false;
    }
});

// Ping Self-Hosted Server (Echo RTT)
dom.btnPingSelfHosted.addEventListener('click', async () => {
    const baseUrl = dom.selfHostedUrl.value.trim().replace(/\/+$/, '');
    if (!baseUrl) return;

    logToConsole(`[PING] Đang gửi GET ${baseUrl}/api/ping...`, 'info');
    const tStart = performance.now();
    try {
        const res = await fetch(`${baseUrl}/api/ping`);
        const data = await res.json();
        const rtt = Math.round(performance.now() - tStart);
        logToConsole(`[PONG] Server trả lời: ${data.message} | RTT: ${rtt}ms | Uptime: ${data.uptimeSeconds}s | IP: ${data.clientIp}`, 'success');
        dom.rttSelfHosted.innerText = `${rtt} ms (Ping)`;
    } catch (err) {
        logToConsole(`[PING ERROR] ${err.message}`, 'error');
    }
});

// Xem Metrics RAM/CPU Self-Hosted Server
dom.btnMetricsSelfHosted.addEventListener('click', async () => {
    const baseUrl = dom.selfHostedUrl.value.trim().replace(/\/+$/, '');
    if (!baseUrl) return;

    try {
        const res = await fetch(`${baseUrl}/api/metrics`);
        const m = await res.json();
        logToConsole(`[METRICS SERVER] RAM Working Set: ${m.memoryWorkingSetMB} MB | RAM Allocated: ${m.memoryAllocatedMB} MB | Luồng: ${m.threadCount} | Tổng Request: ${m.totalRequestsReceived} | OS: ${m.operatingSystem}`, 'metrics');
        dom.bmSelfMemory.innerText = `${m.memoryWorkingSetMB} MB RAM (Đo thực tế)`;
    } catch (err) {
        logToConsole(`[METRICS ERROR] Không lấy được thông tin metrics: ${err.message}`, 'error');
    }
});

// =========================================================================================
// 5. BỘ ĐO LƯỜNG TỰ ĐỘNG & ĐỐI SÁNH HIỆU NĂNG (NGÀY 3 & PHÚT 4-5)
// =========================================================================================
dom.btnRunBenchmark.addEventListener('click', async () => {
    const count = parseInt(dom.benchmarkCount.value, 10);
    const selfUrl = dom.selfHostedUrl.value.trim();
    const supaUrl = dom.supabaseUrl.value.trim();
    const supaKey = dom.supabaseKey.value.trim();

    if (!selfUrl) {
        alert('⚠️ Vui lòng cấu hình Self-Hosted Server URL trước!');
        return;
    }

    const testSupabase = Boolean(supaUrl && supaKey);
    if (!testSupabase) {
        logToConsole('⚠️ Chưa cấu hình Supabase Key/URL -> Chỉ chạy đo phía Self-Hosted Server.', 'info');
    }

    // Đổi trạng thái UI
    dom.btnRunBenchmark.disabled = true;
    dom.clientStatus.className = 'status-pill status-busy';
    dom.clientStatus.innerText = 'Đang đo lường...';
    dom.progressContainer.classList.remove('hidden');
    dom.progressBar.style.width = '0%';
    dom.btnExportCsv.disabled = true;

    latestBenchmarkData = [];
    const selfRtts = [];
    const supaRtts = [];
    let selfSuccess = 0;
    let supaSuccess = 0;

    logToConsole(`=======================================================`, 'info');
    logToConsole(`BẮT ĐẦU BENCHMARK: ${count} requests mỗi bên`, 'info');
    logToConsole(`=======================================================`, 'info');

    const totalSteps = testSupabase ? count * 2 : count;
    let completedSteps = 0;

    for (let i = 1; i <= count; i++) {
        // 1. Đo Self-Hosted
        const selfRes = await sendToSelfHosted(`Benchmark request #${i}`, true);
        if (selfRes.success) {
            selfSuccess++;
            selfRtts.push(selfRes.rtt);
        }
        latestBenchmarkData.push({
            index: i,
            target: 'Self-Hosted',
            rtt_ms: selfRes.rtt,
            status: selfRes.status || 'ERROR',
            timestamp: new Date().toISOString()
        });

        completedSteps++;
        updateProgress(completedSteps, totalSteps, `Đang đo Self-Hosted: ${i}/${count}`);

        // 2. Đo Supabase (nếu có cấu hình)
        if (testSupabase) {
            const supaRes = await sendToSupabase(`Benchmark request #${i}`, true);
            if (supaRes.success) {
                supaSuccess++;
                supaRtts.push(supaRes.rtt);
            }
            latestBenchmarkData.push({
                index: i,
                target: 'Supabase',
                rtt_ms: supaRes.rtt,
                status: supaRes.status || 'ERROR',
                timestamp: new Date().toISOString()
            });

            completedSteps++;
            updateProgress(completedSteps, totalSteps, `Đang đo Supabase: ${i}/${count}`);
        }

        // Nghỉ nhẹ 100ms giữa các request để mô phỏng luồng request thực tế
        await new Promise(r => setTimeout(r, 100));
    }

    // CẬP NHẬT KẾT QUẢ VÀO BẢNG ĐỐI SÁNH
    // 1. Phía Self-Hosted
    if (selfRtts.length > 0) {
        const selfMin = Math.min(...selfRtts);
        const selfMax = Math.max(...selfRtts);
        const selfAvg = Math.round(selfRtts.reduce((a, b) => a + b, 0) / selfRtts.length);
        const selfP95 = calculatePercentile(selfRtts, 95);

        dom.bmSelfMin.innerText = `${selfMin} ms`;
        dom.bmSelfAvg.innerText = `${selfAvg} ms`;
        dom.bmSelfP95.innerText = `${selfP95} ms`;
        dom.bmSelfMax.innerText = `${selfMax} ms`;
        dom.bmSelfSuccess.innerText = `${Math.round((selfSuccess / count) * 100)}% (${selfSuccess}/${count})`;
    }

    // 2. Phía Supabase
    if (supaRtts.length > 0) {
        const supaMin = Math.min(...supaRtts);
        const supaMax = Math.max(...supaRtts);
        const supaAvg = Math.round(supaRtts.reduce((a, b) => a + b, 0) / supaRtts.length);
        const supaP95 = calculatePercentile(supaRtts, 95);

        dom.bmSupabaseMin.innerText = `${supaMin} ms`;
        dom.bmSupabaseAvg.innerText = `${supaAvg} ms`;
        dom.bmSupabaseP95.innerText = `${supaP95} ms`;
        dom.bmSupabaseMax.innerText = `${supaMax} ms`;
        dom.bmSupabaseSuccess.innerText = `${Math.round((supaSuccess / count) * 100)}% (${supaSuccess}/${count})`;
    }

    // Lấy thêm metrics RAM từ server
    try {
        const res = await fetch(`${selfUrl.replace(/\/+$/, '')}/api/metrics`);
        const m = await res.json();
        dom.bmSelfMemory.innerText = `${m.memoryWorkingSetMB} MB RAM (Đo thực tế)`;
    } catch (e) {
        // bỏ qua nếu lỗi
    }

    // Khôi phục UI
    dom.progressText.innerText = 'Hoàn thành đo lường!';
    dom.clientStatus.className = 'status-pill status-ready';
    dom.clientStatus.innerText = 'Đo hoàn tất';
    dom.btnRunBenchmark.disabled = false;
    dom.btnExportCsv.disabled = false;

    logToConsole(`ĐO LƯỜNG HOÀN TẤT! Dữ liệu đã được tổng hợp vào bảng bên trên.`, 'success');
});

function updateProgress(done, total, text) {
    const percent = Math.round((done / total) * 100);
    dom.progressBar.style.width = `${percent}%`;
    dom.progressText.innerText = `${text} (${percent}%)`;
}

// =========================================================================================
// 6. XUẤT DỮ LIỆU ĐO ĐẠC RA CSV
// =========================================================================================
dom.btnExportCsv.addEventListener('click', () => {
    if (latestBenchmarkData.length === 0) return;

    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += 'STT,Target_Server,RTT_ms,HTTP_Status,Timestamp\n';

    latestBenchmarkData.forEach(row => {
        csvContent += `${row.index},"${row.target}",${row.rtt_ms},"${row.status}","${row.timestamp}"\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `NT106_Benchmark_Report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    logToConsole('Đã tải xuống file CSV kết quả đo lường.', 'success');
});

// Khởi chạy khi tải trang
window.addEventListener('DOMContentLoaded', () => {
    loadSavedConfig();
    logToConsole('Giao diện sẵn sàng. Sẵn sàng cho kịch bản Demo Phút 2 & Phút 3.', 'info');
});

