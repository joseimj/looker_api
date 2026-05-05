# Integración Headless Looker y GCIP: Flujo de Autenticación "Sudo"

Este repositorio/directorio contiene la implementación de referencia para autorizar programáticamente a usuarios autenticados mediante **Google Identity Platform (GCIP)** dentro de **Looker Cloud Core**, utilizando una arquitectura 100% *headless*.

El objetivo principal de este código es garantizar el aislamiento de datos (Multi-tenant) aplicando *Access Filters* de LookML basados en el `tenant_id` del usuario, sin requerir que este interactúe con la interfaz gráfica de Looker.

## 🏗️ Arquitectura y Flujo de Trabajo

La solución utiliza el backend como un **Proxy seguro** para evitar exponer los tokens de Looker al cliente web/móvil y evitar redirecciones HTTP 302. El flujo es el siguiente:

1. **Validación GCIP:** El frontend envía el ID Token de GCIP al backend proxy. El backend valida este token y extrae la identidad del usuario (ej. email) y su `tenant_id`.
2. **Aprovisionamiento Dinámico (Looker API):** Usando una *Service Account* con permisos de administrador, el backend busca al usuario en Looker y le inyecta/actualiza su `tenant_id` como un Atributo de Usuario (*User Attribute*).
3. **Impersonación (Flujo Sudo):** La *Service Account* ejecuta un inicio de sesión "Sudo" a nombre de ese usuario para obtener un token de sesión temporal (Bearer Token).
4. **Proxy de Consultas:** El backend utiliza este Bearer Token para solicitar datos a la API de Looker en nombre del usuario y devuelve el JSON resultante al frontend.

## 📋 Requisitos Previos

Para ejecutar este código, el entorno debe contar con lo siguiente:

* **Python 3.8** o superior.
* Librería oficial de Looker instalada:
  ```bash
  pip install looker_sdk
