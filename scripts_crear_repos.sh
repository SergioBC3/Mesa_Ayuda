
set -euo pipefail
USUARIO="${1:?Uso: bash scripts_crear_repos.sh TU_USUARIO_GITHUB}"
RAIZ="$(cd "$(dirname "$0")" && pwd)"

publicar() {            
  local carpeta="$1" repo="$2" tmp
  tmp="$(mktemp -d)"
  cp -r "$RAIZ/$carpeta/." "$tmp/"
  rm -rf "$tmp/node_modules" "$tmp/target" "$tmp/__pycache__"
  ( cd "$tmp" && git init -q -b main && git add . && git commit -q -m "Microservicio $repo" \
    && gh repo create "$USUARIO/$repo" --public --source=. --push )
  echo "Publicado: https://github.com/$USUARIO/$repo"
}

publicar microservicio                              mesa-ayuda-ms-lectura-python
publicar microservicios/ms_lectura_respaldo_node    mesa-ayuda-ms-lectura-respaldo-node
publicar microservicios/ms_insertar_java            mesa-ayuda-ms-insertar-java
publicar microservicios/ms_actualizar_go            mesa-ayuda-ms-actualizar-go
publicar microservicios/ms_eliminar_node            mesa-ayuda-ms-eliminar-node
