# Guía para Crear Pull Request

## Paso 1: Crear Fork en GitHub

1. Abre tu navegador y ve a:
   ```
   https://github.com/stephengpope/no-code-architects-toolkit
   ```

2. Haz clic en el botón **"Fork"** (arriba a la derecha, al lado de "Star")

3. Espera a que GitHub cree tu fork. Esto creará:
   ```
   https://github.com/gneuman/no-code-architects-toolkit
   ```

## Paso 2: Configurar Remote y Push

Una vez creado el fork, ejecuta estos comandos en PowerShell:

```powershell
# Agregar tu fork como remote
git remote add fork https://github.com/gneuman/no-code-architects-toolkit.git

# Verificar que se agregó correctamente
git remote -v

# Push tu branch al fork
git push fork arabic-fonts-feature
```

## Paso 3: Crear Pull Request

Después del push, GitHub te mostrará un link para crear el PR. O puedes:

1. Ve a: https://github.com/stephengpope/no-code-architects-toolkit
2. GitHub mostrará un banner amarillo con "Compare & pull request"
3. O ve a: https://github.com/gneuman/no-code-architects-toolkit
4. Click en **"Pull requests"** → **"New pull request"**
5. Selecciona:
   - **Base repository**: `stephengpope/no-code-architects-toolkit` (main)
   - **Head repository**: `gneuman/no-code-architects-toolkit` (arabic-fonts-feature)
6. Completa el título y descripción del PR
7. Click en **"Create pull request"**

## Título Sugerido para el PR:
```
feat: Add Arabic font support with RTL rendering
```

## Descripción Sugerida:
```markdown
## Summary
This PR adds comprehensive support for Arabic fonts and Right-to-Left (RTL) text rendering in video captions.

## Changes
- Added support for multiple Arabic fonts (Amiri, Cairo, Tajawal, Almarai, Scheherazade, NotoSansArabic)
- Implemented RTL text rendering for Arabic captions
- Added auto-detection of Arabic text for automatic RTL handling
- Fixed highlight style to correctly display sequential word highlighting in RTL mode
- Updated font detection to support local fonts directory on Windows
- Added font name to output filename (captioned_{fontname}.mp4)

## Testing
- Tested with multiple Arabic fonts
- Verified RTL rendering works correctly
- Tested on Windows local environment

## Files Changed
- `routes/v1/video/caption_video.py` - Added RTL parameter to schema
- `services/ass_toolkit.py` - Implemented RTL logic and auto-detection
- `services/caption_video.py` - Updated font detection and output filename
- `fonts/*.ttf` - Added 27 Arabic font files
- `.gitignore` - Updated to exclude development files
```

