document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const fileInput = document.getElementById('id_images');
    if (fileInput) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'file-preview';
        fileInput.after(previewContainer);

        fileInput.addEventListener('change', function(e) {
            previewContainer.innerHTML = '';
            const files = e.target.files;

            if (files.length > 10) {
                alert('You can upload a maximum of 10 files');
                fileInput.value = '';
                return;
            }

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const previewItem = document.createElement('div');
                        previewItem.className = 'file-preview-item';
                        previewItem.innerHTML = `
                            <img src="${e.target.result}" alt="${file.name}">
                            <span>${file.name}</span>
                        `;
                        previewContainer.appendChild(previewItem);
                    }
                    reader.readAsDataURL(file);
                }
            }
        });
    }

    // Smooth page transitions
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '0';
        setTimeout(() => {
            mainContent.style.transition = 'opacity 0.3s ease';
            mainContent.style.opacity = '1';
        }, 50);
    }

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });

    // Responsive navigation for mobile
    const nav = document.querySelector('nav');
    if (nav && window.innerWidth < 768) {
        const navToggle = document.createElement('button');
        navToggle.className = 'nav-toggle';
        navToggle.innerHTML = '<i class="fas fa-bars"></i>';
        nav.insertBefore(navToggle, nav.firstChild);

        let isOpen = false;
        navToggle.addEventListener('click', function() {
            isOpen = !isOpen;
            const links = nav.querySelectorAll('a:not(.nav-toggle)');
            links.forEach(link => {
                link.style.display = isOpen ? 'block' : 'none';
            });
        });

        // Hide links initially on mobile
        const links = nav.querySelectorAll('a:not(.nav-toggle)');
        links.forEach(link => {
            link.style.display = 'none';
        });
    }

    // Auto-hide messages after 5 seconds
    const messages = document.querySelector('.messages');
    if (messages) {
        setTimeout(() => {
            messages.style.transition = 'opacity 0.5s ease';
            messages.style.opacity = '0';
            setTimeout(() => {
                messages.remove();
            }, 500);
        }, 5000);
    }

    // Image modal for prediction details
    const detailImages = document.querySelectorAll('.detail-image');
    detailImages.forEach(img => {
        img.addEventListener('click', function() {
            const modal = document.createElement('div');
            modal.className = 'image-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close-modal">&times;</span>
                    <img src="${this.src}" alt="Enlarged view">
                </div>
            `;
            document.body.appendChild(modal);

            modal.querySelector('.close-modal').addEventListener('click', function() {
                modal.style.opacity = '0';
                setTimeout(() => {
                    modal.remove();
                }, 300);
            });
        });
    });

    // Add a back to top button
    const backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    document.body.appendChild(backToTop);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
        } else {
            backToTop.style.display = 'none';
        }
    });

    backToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Add image modal styles dynamically
const modalStyles = document.createElement('style');
modalStyles.textContent = `
    .image-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        opacity: 1;
        transition: opacity 0.3s ease;
    }
    
    .modal-content {
        position: relative;
        max-width: 90%;
        max-height: 90%;
    }
    
    .modal-content img {
        max-width: 100%;
        max-height: 80vh;
        display: block;
    }
    
    .close-modal {
        position: absolute;
        top: -40px;
        right: 0;
        color: white;
        font-size: 35px;
        cursor: pointer;
    }
    
    .back-to-top {
        position: fixed;
        bottom: 80px;
        right: 20px;
        background: #6a2c5e;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        cursor: pointer;
        display: none;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        z-index: 99;
    }
    
    .back-to-top:hover {
        background: #4a1c40;
        transform: translateY(-3px);
    }
`;
document.head.appendChild(modalStyles);

// Handle displaying popup messages
document.addEventListener('DOMContentLoaded', function() {
    // Check for failed predictions in the template context
    const failedPredictions = JSON.parse('{{ failed_predictions|escapejs }}') || [];

    failedPredictions.forEach(failure => {
        if (failure.show_popup) {
            showPopupNotification(
                failure.popup_message || failure.error,
                failure.popup_duration || 120000
            );
        }
    });

    function showPopupNotification(message, duration) {
        const popup = document.createElement('div');
        popup.className = 'custom-popup-notification';
        popup.innerHTML = `
            <div class="popup-content">
                <span class="popup-message">${message}</span>
                <button class="popup-close-btn">&times;</button>
            </div>
        `;

        document.body.appendChild(popup);

        // Auto-remove after duration
        const timeout = setTimeout(() => {
            popup.remove();
        }, duration);

        // Manual close
        popup.querySelector('.popup-close-btn').addEventListener('click', () => {
            clearTimeout(timeout);
            popup.remove();
        });
    }
});