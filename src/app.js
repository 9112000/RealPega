        document.addEventListener('DOMContentLoaded', function() {
            const isTelegramWebApp = window.Telegram?.WebApp?.initData !== undefined;
            
            if (isTelegramWebApp) {
                document.body.classList.add('tg-webapp');
                document.getElementById('modalHeader').style.display = 'none';
            }
            
            const previewModal = document.getElementById('previewModal');
            const closePreviewModal = document.getElementById('closePreviewModal');
            const previewFrame = document.getElementById('preview-frame');
            const modalTitle = document.getElementById('modalTitle');
            const loader = document.getElementById('loader');
            const modalHeader = document.getElementById('modalHeader');
            const optionButtons = document.querySelectorAll('.option-btn');
            
            function openModal(title, src) {
                modalTitle.textContent = title;
                loader.style.display = "block";
                previewFrame.style.display = "none";
                previewFrame.src = src;
                previewModal.classList.add('active');
                document.body.style.overflow = 'hidden';
                
                if (isTelegramWebApp) {
                    const tg = Telegram.WebApp;
                    tg.BackButton.show();
                    tg.BackButton.onClick(closeModal);
                }
            }
            
            function closeModal() {
                previewModal.classList.remove('active');
                previewFrame.src = "";
                document.body.style.overflow = 'auto';
                
                if (isTelegramWebApp) {
                    Telegram.WebApp.BackButton.hide();
                }
            }
            
            optionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const title = this.getAttribute('data-title');
                    const url = this.getAttribute('data-url');
                    openModal(title, url);
                });
            });
            
            closePreviewModal.addEventListener('click', closeModal);
            
            previewFrame.addEventListener('load', function() {
                loader.style.display = "none";
                previewFrame.style.display = "block";
            });
            
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') closeModal();
            });
            
            
            if (isTelegramWebApp) {
                const tg = Telegram.WebApp;
                tg.ready();
                tg.expand();
                tg.setHeaderColor("#0d1117");
                modalHeader.style.display = 'none';
                tg.BackButton.hide();
            }
        });
