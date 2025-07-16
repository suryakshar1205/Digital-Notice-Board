/**
 * PDF Viewer JavaScript
 * Handles PDF preview functionality with modal display and error handling
 */

class PDFViewer {
    constructor() {
        this.modal = null;
        this.currentPdfUrl = null;
        this.init();
    }

    init() {
        // Create modal HTML
        this.createModal();
        
        // Bind event listeners
        this.bindEvents();
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }

    createModal() {
        const modalHTML = `
            <div id="pdfModal" class="pdf-modal">
                <div class="pdf-modal-content">
                    <div class="pdf-modal-header">
                        <h3 class="pdf-modal-title">
                            <i class="fas fa-file-pdf"></i>
                            <span id="pdfModalTitle">PDF Preview</span>
                        </h3>
                        <button class="pdf-modal-close" id="pdfModalClose">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="pdf-modal-body" id="pdfModalBody">
                        <div class="pdf-loading">
                            <div class="pdf-loading-spinner"></div>
                            <p>Loading PDF...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('pdfModal');
    }

    bindEvents() {
        // Close button
        document.getElementById('pdfModalClose').addEventListener('click', () => {
            this.closeModal();
        });

        // Click outside modal to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });
    }

    showPdf(pdfUrl, title = 'PDF Document') {
        this.currentPdfUrl = pdfUrl;
        document.getElementById('pdfModalTitle').textContent = title;
        
        // Show loading state
        this.showLoading();
        
        // Show modal
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Load PDF
        this.loadPdf(pdfUrl);
    }

    showLoading() {
        const modalBody = document.getElementById('pdfModalBody');
        modalBody.innerHTML = `
            <div class="pdf-loading">
                <div class="pdf-loading-spinner"></div>
                <p>Loading PDF...</p>
            </div>
        `;
    }

    showError(message, downloadUrl = null) {
        const modalBody = document.getElementById('pdfModalBody');
        let downloadButton = '';
        
        if (downloadUrl) {
            downloadButton = `
                <a href="${downloadUrl}" class="btn" download>
                    <i class="fas fa-download me-2"></i>Download PDF
                </a>
            `;
        }
        
        modalBody.innerHTML = `
            <div class="pdf-error">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Unable to Preview PDF</h4>
                <p>${message}</p>
                ${downloadButton}
            </div>
        `;
    }

    loadPdf(pdfUrl) {
        const modalBody = document.getElementById('pdfModalBody');
        
        // Create iframe for PDF display
        const iframe = document.createElement('iframe');
        iframe.className = 'pdf-iframe';
        iframe.src = pdfUrl;
        
        // Handle iframe load events
        iframe.onload = () => {
            // Check if PDF loaded successfully
            try {
                // Try to access iframe content to check for errors
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                if (iframeDoc.body && iframeDoc.body.innerHTML.includes('error')) {
                    this.showError('The PDF could not be loaded. It may be corrupted or not accessible.');
                }
            } catch (e) {
                // Cross-origin restrictions - assume it loaded fine
                // console.log('PDF loaded successfully');
            }
        };
        
        iframe.onerror = () => {
            this.showError('Failed to load PDF. Please try downloading the file instead.');
        };
        
        // Set timeout for loading
        setTimeout(() => {
            if (modalBody.querySelector('.pdf-loading')) {
                // Still showing loading, replace with iframe
                modalBody.innerHTML = '';
                modalBody.appendChild(iframe);
            }
        }, 1000);
        
        // Replace loading with iframe
        modalBody.innerHTML = '';
        modalBody.appendChild(iframe);
    }

    closeModal() {
        this.modal.classList.remove('show');
        document.body.style.overflow = '';
        this.currentPdfUrl = null;
        
        // Clear modal content
        const modalBody = document.getElementById('pdfModalBody');
        modalBody.innerHTML = `
            <div class="pdf-loading">
                <div class="pdf-loading-spinner"></div>
                <p>Loading PDF...</p>
            </div>
        `;
    }
}

// Initialize PDF viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pdfViewer = new PDFViewer();
    
    // Add click handlers to PDF preview buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('pdf-preview-btn') || e.target.closest('.pdf-preview-btn')) {
            e.preventDefault();
            
            const button = e.target.classList.contains('pdf-preview-btn') ? e.target : e.target.closest('.pdf-preview-btn');
            const pdfUrl = button.getAttribute('data-pdf-url');
            const title = button.getAttribute('data-title') || 'PDF Document';
            
            if (pdfUrl) {
                window.pdfViewer.showPdf(pdfUrl, title);
            }
        }
    });
});

// Utility function to create PDF preview buttons
function createPdfPreviewButton(filename, title) {
    const pdfUrl = `/preview_pdf/${encodeURIComponent(filename)}`;
    const downloadUrl = `/download_notice/${encodeURIComponent(filename)}`;
    
    return `
        <button class="pdf-preview-btn" data-pdf-url="${pdfUrl}" data-title="${title}" title="Preview PDF">
            <i class="fas fa-eye"></i>Preview
        </button>
        <a href="${downloadUrl}" class="btn btn-sm btn-outline-primary" download title="Download PDF">
            <i class="fas fa-download me-1"></i>Download
        </a>
    `;
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { PDFViewer, createPdfPreviewButton };
} 