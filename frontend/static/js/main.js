
// ChemPatent Pro - 前端JavaScript

// 全局變量
let currentAnalysisType = null;
let analysisResults = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupScrollSpy();
});

// 初始化應用
function initializeApp() {
    console.log('ChemPatent Pro 已加載');

    // 檢查API可用性
    checkAPIHealth();

    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 設置事件監聽器
function setupEventListeners() {
    // 表單提交事件
    document.getElementById('comprehensiveForm').addEventListener('submit', handleComprehensiveAnalysis);
    document.getElementById('pdfForm').addEventListener('submit', handlePDFAnalysis);
    document.getElementById('chemistryForm').addEventListener('submit', handleChemistryAnalysis);
    document.getElementById('patentForm').addEventListener('submit', handlePatentAnalysis);
    document.getElementById('molecularForm').addEventListener('submit', handleMolecularAnalysis);

    // 導航事件
    document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 設置滾動監聽
function setupScrollSpy() {
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.backgroundColor = 'rgba(44, 90, 160, 0.95)';
        } else {
            navbar.style.backgroundColor = '';
        }
    });
}

// 滾動到分析區域
function scrollToAnalysis() {
    document.getElementById('analysis').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// 檢查API健康狀態
async function checkAPIHealth() {
    try {
        const response = await axios.get('/api/v1/health');
        console.log('API狀態正常:', response.data);
        showNotification('系統已就緒', 'success');
    } catch (error) {
        console.error('API連接失敗:', error);
        showNotification('API連接失敗，部分功能可能不可用', 'warning');
    }
}

// 顯示通知
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';

    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // 自動移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, duration);
}

// 顯示加載指示器
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsContainer').innerHTML = '';

    // 滾動到結果區域
    document.getElementById('results').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// 隱藏加載指示器
function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}


// 綜合分析處理
async function handleComprehensiveAnalysis(e) {
    e.preventDefault();

    const formData = new FormData();
    const file = document.getElementById('comprehensiveFile').files[0];
    const language = document.getElementById('comprehensiveLanguage').value;
    const includeMolecular = document.getElementById('includeMolecular').checked;
    const includePatent = document.getElementById('includePatent').checked;

    if (!file) {
        showNotification('請選擇PDF文件', 'warning');
        return;
    }

    formData.append('pdf_file', file);
    formData.append('language', language);
    formData.append('include_molecular_analysis', includeMolecular);
    formData.append('include_patent_analysis', includePatent);

    currentAnalysisType = 'comprehensive';
    showLoading();

    try {
        const response = await axios.post('/api/v1/comprehensive-analysis', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        analysisResults = response.data;
        displayComprehensiveResults(response.data);
        showNotification('綜合分析完成', 'success');

    } catch (error) {
        console.error('綜合分析錯誤:', error);
        showNotification('綜合分析失敗: ' + (error.response?.data?.detail || error.message), 'danger');
        displayErrorResults(error);
    } finally {
        hideLoading();
    }
}

// PDF分析處理
async function handlePDFAnalysis(e) {
    e.preventDefault();

    const formData = new FormData();
    const file = document.getElementById('pdfFile').files[0];
    const language = document.getElementById('pdfLanguage').value;

    if (!file) {
        showNotification('請選擇PDF文件', 'warning');
        return;
    }

    formData.append('file', file);
    formData.append('language', language);

    currentAnalysisType = 'pdf';
    showLoading();

    try {
        const response = await axios.post('/api/v1/parse-pdf', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        analysisResults = response.data;
        displayPDFResults(response.data);
        showNotification('PDF解析完成', 'success');

    } catch (error) {
        console.error('PDF分析錯誤:', error);
        showNotification('PDF分析失敗: ' + (error.response?.data?.detail || error.message), 'danger');
        displayErrorResults(error);
    } finally {
        hideLoading();
    }
}

// 化學分析處理
async function handleChemistryAnalysis(e) {
    e.preventDefault();

    const formData = new FormData();
    const text = document.getElementById('chemistryText').value;
    const image = document.getElementById('chemistryImage').files[0];

    if (!text && !image) {
        showNotification('請輸入文本或上傳圖像', 'warning');
        return;
    }

    if (text) formData.append('text', text);
    if (image) formData.append('image', image);

    currentAnalysisType = 'chemistry';
    showLoading();

    try {
        const response = await axios.post('/api/v1/analyze-chemistry', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        analysisResults = response.data;
        displayChemistryResults(response.data);
        showNotification('化學分析完成', 'success');

    } catch (error) {
        console.error('化學分析錯誤:', error);
        showNotification('化學分析失敗: ' + (error.response?.data?.detail || error.message), 'danger');
        displayErrorResults(error);
    } finally {
        hideLoading();
    }
}

// 專利分析處理
async function handlePatentAnalysis(e) {
    e.preventDefault();

    const text = document.getElementById('patentText').value;
    const language = document.getElementById('patentLanguage').value;

    if (!text.trim()) {
        showNotification('請輸入專利文本', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('text', text);
    formData.append('language', language);

    currentAnalysisType = 'patent';
    showLoading();

    try {
        const response = await axios.post('/api/v1/analyze-patent-claims', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        analysisResults = response.data;
        displayPatentResults(response.data);
        showNotification('專利分析完成', 'success');

    } catch (error) {
        console.error('專利分析錯誤:', error);
        showNotification('專利分析失敗: ' + (error.response?.data?.detail || error.message), 'danger');
        displayErrorResults(error);
    } finally {
        hideLoading();
    }
}

// 分子性質分析處理
async function handleMolecularAnalysis(e) {
    e.preventDefault();

    const smilesText = document.getElementById('smilesInput').value;

    if (!smilesText.trim()) {
        showNotification('請輸入SMILES字符串', 'warning');
        return;
    }

    const smilesList = smilesText.split('\n').filter(line => line.trim());

    if (smilesList.length === 0) {
        showNotification('請輸入有效的SMILES字符串', 'warning');
        return;
    }

    const formData = new FormData();
    smilesList.forEach(smiles => {
        formData.append('smiles_list', smiles.trim());
    });

    currentAnalysisType = 'molecular';
    showLoading();

    try {
        const response = await axios.post('/api/v1/calculate-molecular-properties', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        analysisResults = response.data;
        displayMolecularResults(response.data);
        showNotification('分子性質計算完成', 'success');

    } catch (error) {
        console.error('分子分析錯誤:', error);
        showNotification('分子分析失敗: ' + (error.response?.data?.detail || error.message), 'danger');
        displayErrorResults(error);
    } finally {
        hideLoading();
    }
}


// 顯示綜合分析結果
function displayComprehensiveResults(data) {
    const container = document.getElementById('resultsContainer');

    let html = `
        <div class="result-card fade-in-up">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3><i class="fas fa-magic text-primary me-2"></i>綜合分析結果</h3>
                <button class="btn btn-outline-primary btn-sm" onclick="downloadResults()">
                    <i class="fas fa-download me-1"></i>下載報告
                </button>
            </div>

            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">${data.pdf_analysis?.page_count || 0}</div>
                        <div class="stat-label">頁面數</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">${data.chemical_analysis?.molecules_found || 0}</div>
                        <div class="stat-label">發現分子</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">${data.patent_analysis?.total_claims || 0}</div>
                        <div class="stat-label">權利要求</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stat-card">
                        <div class="stat-number">${data.pdf_analysis?.language?.toUpperCase() || 'N/A'}</div>
                        <div class="stat-label">檢測語言</div>
                    </div>
                </div>
            </div>
    `;

    // PDF分析結果
    if (data.pdf_analysis) {
        html += createPDFResultSection(data.pdf_analysis);
    }

    // 化學分析結果
    if (data.chemical_analysis) {
        html += createChemistryResultSection(data.chemical_analysis);
    }

    // 專利分析結果
    if (data.patent_analysis) {
        html += createPatentResultSection(data.patent_analysis);
    }

    // 分子性質結果
    if (data.molecular_properties) {
        html += createMolecularResultSection(data.molecular_properties);
    }

    html += '</div>';
    container.innerHTML = html;
}

// 顯示PDF結果
function displayPDFResults(data) {
    const container = document.getElementById('resultsContainer');
    const html = `
        <div class="result-card fade-in-up">
            <h3><i class="fas fa-file-pdf text-danger me-2"></i>PDF解析結果</h3>
            ${createPDFResultSection(data)}
        </div>
    `;
    container.innerHTML = html;
}

// 顯示化學分析結果
function displayChemistryResults(data) {
    const container = document.getElementById('resultsContainer');
    const html = `
        <div class="result-card fade-in-up">
            <h3><i class="fas fa-atom text-success me-2"></i>化學結構分析結果</h3>
            ${createChemistryResultSection(data)}
        </div>
    `;
    container.innerHTML = html;
}

// 顯示專利分析結果
function displayPatentResults(data) {
    const container = document.getElementById('resultsContainer');
    const html = `
        <div class="result-card fade-in-up">
            <h3><i class="fas fa-balance-scale text-warning me-2"></i>專利權利要求分析結果</h3>
            ${createPatentResultSection(data)}
        </div>
    `;
    container.innerHTML = html;
}

// 顯示分子性質結果
function displayMolecularResults(data) {
    const container = document.getElementById('resultsContainer');
    const html = `
        <div class="result-card fade-in-up">
            <h3><i class="fas fa-chart-bar text-info me-2"></i>分子性質計算結果</h3>
            ${createMolecularResultSection(data)}
        </div>
    `;
    container.innerHTML = html;
}

// 創建PDF結果部分
function createPDFResultSection(data) {
    return `
        <div class="result-section">
            <h4><i class="fas fa-info-circle me-2"></i>文檔信息</h4>
            <div class="row">
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr><td><strong>文件名:</strong></td><td>${data.filename}</td></tr>
                        <tr><td><strong>頁面數:</strong></td><td>${data.page_count}</td></tr>
                        <tr><td><strong>語言:</strong></td><td>${data.language}</td></tr>
                        <tr><td><strong>提取方法:</strong></td><td>${data.extraction_method}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <table class="table table-borderless">
                        <tr><td><strong>作者:</strong></td><td>${data.metadata?.author || 'N/A'}</td></tr>
                        <tr><td><strong>標題:</strong></td><td>${data.metadata?.title || 'N/A'}</td></tr>
                        <tr><td><strong>創建日期:</strong></td><td>${data.metadata?.creation_date || 'N/A'}</td></tr>
                    </table>
                </div>
            </div>

            <h5><i class="fas fa-file-alt me-2"></i>文檔結構</h5>
            <div class="row">
                <div class="col-md-4">
                    <div class="text-center">
                        <div class="h4 text-primary">${data.structure?.headings?.length || 0}</div>
                        <div>標題</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <div class="h4 text-success">${data.structure?.sections?.length || 0}</div>
                        <div>段落</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="text-center">
                        <div class="h4 text-info">${data.structure?.tables?.length || 0}</div>
                        <div>表格</div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 創建化學分析結果部分
function createChemistryResultSection(data) {
    let html = `
        <div class="result-section">
            <h4><i class="fas fa-flask me-2"></i>化學分析摘要</h4>
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-primary">${data.molecules_found}</div>
                        <div>發現分子</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-success">${data.smiles?.length || 0}</div>
                        <div>SMILES</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-warning">${data.functional_groups?.length || 0}</div>
                        <div>官能團</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-info">${data.chemical_names?.length || 0}</div>
                        <div>化學名稱</div>
                    </div>
                </div>
            </div>
    `;

    // SMILES列表
    if (data.smiles && data.smiles.length > 0) {
        html += `
            <h5><i class="fas fa-code me-2"></i>SMILES字符串</h5>
            <div class="mb-4">
        `;
        data.smiles.forEach((smiles, index) => {
            html += `
                <div class="d-flex justify-content-between align-items-center p-3 mb-2 bg-light rounded">
                    <code class="text-primary">${smiles}</code>
                    <button class="btn btn-sm btn-outline-info" onclick="viewMoleculeImage('${smiles}')">
                        <i class="fas fa-eye me-1"></i>查看結構
                    </button>
                </div>
            `;
        });
        html += '</div>';
    }

    // 官能團
    if (data.functional_groups && data.functional_groups.length > 0) {
        html += `
            <h5><i class="fas fa-tags me-2"></i>檢測到的官能團</h5>
            <div class="mb-4">
        `;
        data.functional_groups.forEach(group => {
            html += `<span class="badge bg-secondary me-2 mb-2">${group}</span>`;
        });
        html += '</div>';
    }

    html += '</div>';
    return html;
}

// 查看分子結構圖
function viewMoleculeImage(smiles) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">分子結構 - ${smiles}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body text-center">
                    <img src="/api/v1/molecule-image/${encodeURIComponent(smiles)}" 
                         class="img-fluid molecule-image" alt="分子結構圖">
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}


// 創建專利分析結果部分
function createPatentResultSection(data) {
    let html = `
        <div class="result-section">
            <h4><i class="fas fa-gavel me-2"></i>專利分析摘要</h4>
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-primary">${data.total_claims}</div>
                        <div>權利要求總數</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-success">${data.structure_analysis?.independent_claims?.length || 0}</div>
                        <div>獨立權利要求</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-warning">${data.structure_analysis?.dependent_claims?.length || 0}</div>
                        <div>依賴權利要求</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-info">${data.potential_issues?.length || 0}</div>
                        <div>潛在問題</div>
                    </div>
                </div>
            </div>
    `;

    // 權利要求列表
    if (data.claims && data.claims.length > 0) {
        html += `
            <h5><i class="fas fa-list me-2"></i>權利要求詳情</h5>
            <div class="accordion mb-4" id="claimsAccordion">
        `;

        data.claims.slice(0, 5).forEach((claim, index) => {
            const typeColor = claim.type === 'product' ? 'primary' : 
                             claim.type === 'method' ? 'success' : 
                             claim.type === 'use' ? 'warning' : 'info';

            html += `
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#claim${index}">
                            權利要求 ${claim.number} 
                            <span class="badge bg-${typeColor} ms-2">${claim.type}</span>
                            <span class="badge bg-secondary ms-2">${claim.word_count} 詞</span>
                        </button>
                    </h2>
                    <div id="claim${index}" class="accordion-collapse collapse" 
                         data-bs-parent="#claimsAccordion">
                        <div class="accordion-body">
                            <p>${claim.text}</p>
                            <small class="text-muted">複雜度分數: ${claim.complexity_score}</small>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';

        if (data.claims.length > 5) {
            html += `<p class="text-muted">顯示前5個權利要求，共${data.claims.length}個</p>`;
        }
    }

    // 建議和問題
    if (data.suggestions && data.suggestions.length > 0) {
        html += `
            <h5><i class="fas fa-lightbulb me-2"></i>改進建議</h5>
            <ul class="list-group mb-4">
        `;
        data.suggestions.forEach(suggestion => {
            html += `<li class="list-group-item"><i class="fas fa-check text-success me-2"></i>${suggestion}</li>`;
        });
        html += '</ul>';
    }

    html += '</div>';
    return html;
}

// 創建分子性質結果部分
function createMolecularResultSection(data) {
    let html = `
        <div class="result-section">
            <h4><i class="fas fa-atom me-2"></i>分子性質摘要</h4>
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-primary">${data.molecules_count}</div>
                        <div>分子數量</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-success">${data.properties_summary?.compliance_rates?.lipinski || 0}</div>
                        <div>Lipinski合規率</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-warning">${Object.keys(data.comparisons?.similarity_matrix || {}).length}</div>
                        <div>相似性比較</div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <div class="h4 text-info">${Object.keys(data.visualizations || {}).length}</div>
                        <div>可視化圖表</div>
                    </div>
                </div>
            </div>
    `;

    // 分子列表
    if (data.molecules && data.molecules.length > 0) {
        html += `
            <h5><i class="fas fa-table me-2"></i>分子性質詳情</h5>
            <div class="table-responsive mb-4">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>分子ID</th>
                            <th>SMILES</th>
                            <th>分子量</th>
                            <th>LogP</th>
                            <th>TPSA</th>
                            <th>HBD</th>
                            <th>HBA</th>
                            <th>QED分數</th>
                            <th>Lipinski</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        data.molecules.forEach(mol => {
            const lipinski = mol.drug_like_properties?.lipinski_compliant;
            html += `
                <tr>
                    <td>${mol.id}</td>
                    <td><code>${mol.smiles}</code></td>
                    <td>${mol.basic_properties?.molecular_weight || 'N/A'}</td>
                    <td>${mol.physicochemical_properties?.logp || 'N/A'}</td>
                    <td>${mol.physicochemical_properties?.tpsa || 'N/A'}</td>
                    <td>${mol.physicochemical_properties?.hbd || 'N/A'}</td>
                    <td>${mol.physicochemical_properties?.hba || 'N/A'}</td>
                    <td>${mol.drug_like_properties?.qed_score || 'N/A'}</td>
                    <td>
                        <span class="badge ${lipinski ? 'bg-success' : 'bg-danger'}">
                            ${lipinski ? '合規' : '不合規'}
                        </span>
                    </td>
                </tr>
            `;
        });

        html += `
                    </tbody>
                </table>
            </div>
        `;
    }

    // 可視化圖表
    if (data.visualizations && Object.keys(data.visualizations).length > 0) {
        html += `
            <h5><i class="fas fa-chart-bar me-2"></i>可視化圖表</h5>
            <div class="row">
        `;

        Object.entries(data.visualizations).forEach(([key, chart]) => {
            if (chart && typeof chart === 'string') {
                html += `
                    <div class="col-12 mb-4">
                        <div class="chart-container">
                            <h6>${getChartTitle(key)}</h6>
                            ${chart}
                        </div>
                    </div>
                `;
            }
        });

        html += '</div>';
    }

    html += '</div>';
    return html;
}

// 獲取圖表標題
function getChartTitle(key) {
    const titles = {
        'property_distributions': '性質分布圖',
        'radar_charts': '分子性質雷達圖',
        'correlation_heatmap': '性質相關性熱力圖',
        'drug_likeness_analysis': '類藥性分析',
        'admet_predictions': 'ADMET預測結果'
    };
    return titles[key] || key;
}

// 顯示錯誤結果
function displayErrorResults(error) {
    const container = document.getElementById('resultsContainer');
    const html = `
        <div class="result-card fade-in-up">
            <div class="alert alert-danger">
                <h4><i class="fas fa-exclamation-triangle me-2"></i>分析失敗</h4>
                <p><strong>錯誤信息:</strong> ${error.response?.data?.detail || error.message}</p>
                <hr>
                <p class="mb-0">請檢查輸入數據或稍後重試。如問題持續存在，請聯繫技術支持。</p>
            </div>
        </div>
    `;
    container.innerHTML = html;
}

// 下載結果報告
function downloadResults() {
    if (!analysisResults) {
        showNotification('沒有可下載的結果', 'warning');
        return;
    }

    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `chempatent_analysis_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
    showNotification('報告已下載', 'success');
}

// 工具函數
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    try {
        return new Date(dateString).toLocaleDateString('zh-TW');
    } catch {
        return dateString;
    }
}

// 複製到剪貼板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('已複製到剪貼板', 'success', 1000);
    }).catch(() => {
        showNotification('複製失敗', 'danger');
    });
}

// 導出數據為CSV
function exportToCSV(data, filename) {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

console.log('ChemPatent Pro JavaScript 載入完成');
