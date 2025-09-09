function overlayBoxData(scriptId, imageId) {
    return {
        detections: [],
        selectedCellIndex: '',
        imageLoaded: false,
        imgNaturalWidth: 0,
        imgNaturalHeight: 0,
        redrawKey: 0,
        visibleClasses: {1: true, 2: true, 3: true},
        showVitResult: false,
        vitResult: null,
        vitCropImage: null,

        init() {
            const img = this.$refs.mainImage;

            this.$nextTick(() => {
                // Aguarda a imagem renderizar
                const dataScript = document.getElementById(scriptId);
                if (dataScript) {
                    this.detections = JSON.parse(dataScript.textContent);
                }

                const updateDimensions = () => {
                    if (img && img.naturalWidth > 0 && img.naturalHeight > 0) {
                        this.imgNaturalWidth = img.naturalWidth;
                        this.imgNaturalHeight = img.naturalHeight;
                        this.redrawKey++;
                        this.detections = [...this.detections]; // Força reatividade
                    }
                };

                // Espera mais um tick se necessário
                setTimeout(() => {
                    updateDimensions();

                    if (typeof ResizeObserver !== 'undefined' && img) {
                        const observer = new ResizeObserver(() => {
                            updateDimensions();
                        });
                        observer.observe(img);
                    } else {
                        window.addEventListener('resize', updateDimensions);
                    }
                }, 50);  // atraso leve para garantir render
            });
        },

        handleBoxClick(det) {
            const apiUrl = document.getElementById('analyzeCellUrl').value;

            fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    image_id: imageId,  // passado no x-data
                    box: det.box        // coordenadas da célula
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.result) {
                        this.showVitResult = true;
                        this.vitResult = data.result.classification;

                        // Checa se vem com base64 ou URL
                        if (data.result.cropped_image.startsWith('data:image')) {
                            this.vitCropImage = data.result.cropped_image;
                        } else {
                            // Adiciona domain se for URL relativa
                            this.vitCropImage = data.result.cropped_image.startsWith('http')
                                ? data.result.cropped_image
                                : window.location.origin + data.result.cropped_image;
                        }
                    } else {
                        alert("Error: " + (data.error || "Unknown"));
                    }
                })
        },

        getBoxStyle(box, label) {
            const img = this.$refs.mainImage;
            if (!img || this.imgNaturalWidth < 1 || this.imgNaturalHeight < 1) return 'display:none;';

            const scaleX = img.clientWidth / this.imgNaturalWidth;
            const scaleY = img.clientHeight / this.imgNaturalHeight;
            const [xMin, yMin, xMax, yMax] = box;

            const paddingX = 5;
            const paddingY = 5;

            let left = (xMin * scaleX) - paddingX;
            let top = (yMin * scaleY) - paddingY;
            let width = (xMax - xMin) * scaleX + (2 * paddingX);
            let height = (yMax - yMin) * scaleY + (2 * paddingY);

            // Clamp para impedir que ultrapasse os limites da imagem
            left = Math.max(0, left);
            top = Math.max(0, top);
            if (left + width > img.clientWidth) {
                width = img.clientWidth - left;
            }
            if (top + height > img.clientHeight) {
                height = img.clientHeight - top;
            }

            let colorMap = {
                1: 'rgba(0, 123, 255, 0.3)',
                2: 'rgba(40, 167, 69, 0.3)',
                3: 'rgba(111, 66, 193, 0.3)'
            };

            let borderColorMap = {
                1: 'blue',
                2: 'green',
                3: 'purple'
            };

            let background = colorMap[label] || 'rgba(255, 255, 255, 0.2)';
            let border = borderColorMap[label] || 'gray';

            return `
                    position: absolute;
                    left: ${left}px;
                    top: ${top}px;
                    width: ${width}px;
                    height: ${height}px;
                    border: 2px solid ${border};
                    background-color: ${background};
                    cursor: pointer;
                    pointer-events: auto;
                    border-radius: 2px;
            `;
        }
        ,

        getLabelStyle(box) {
            const img = this.$refs.mainImage;
            if (!img || this.imgNaturalWidth < 1 || this.imgNaturalHeight < 1) return 'display:none;';

            const scaleX = img.clientWidth / this.imgNaturalWidth;
            const scaleY = img.clientHeight / this.imgNaturalHeight;
            const [xMin, yMin] = box;

            const padding = 4;
            const labelHeight = 16;
            const labelWidthEstimate = 90;  // estimativa do comprimento em px

            let left = xMin * scaleX;
            let top = (yMin * scaleY) - labelHeight;

            // Corrigir se o topo está fora da imagem
            if (top < 0) {
                top = (yMin * scaleY) + padding;
            }

            // Corrigir se a label está muito à direita
            if ((left + labelWidthEstimate) > img.clientWidth) {
                left = img.clientWidth - labelWidthEstimate - padding;
            }

            return `
                position: absolute;
                left: ${left}px;
                top: ${top}px;
                z-index: 10;
                font-size: 11px;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 1px 4px;
                border-radius: 3px;
                white-space: nowrap;`;
        }
    };
}
