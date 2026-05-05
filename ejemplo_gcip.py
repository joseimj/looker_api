import looker_sdk
from looker_sdk import models40 as models

# Inicializa el cliente del SDK de Looker usando tu Service Account (lee de looker.ini o variables de entorno)
sdk = looker_sdk.init40()

def get_looker_sudo_token(gcip_email: str, gcip_tenant_id: str, tenant_attribute_id: int) -> str:
    """
    Busca al usuario, actualiza su tenant_id y ejecuta Sudo para obtener su token.
    """
    try:
        # 1. Buscar al usuario en Looker mediante su correo de GCIP
        users = sdk.search_users(email=gcip_email)
       
        if not users:
            # Si es un entorno 100% headless, aquí puedes crear al usuario programáticamente
            # usando sdk.create_user(models.WriteUser(...))
            raise Exception(f"Usuario {gcip_email} no encontrado en Looker.")
       
        looker_user_id = users[0].id

        # 2. Actualizar el User Attribute (tenant_id) ANTES de iniciar sesión
        # Esto garantiza que los Access Filters de LookML apliquen la seguridad a nivel de fila correcta.
        sdk.set_user_attribute_user_value(
            user_id=looker_user_id,
            user_attribute_id=tenant_attribute_id,
            body=models.WriteUserAttributeWithValue(
                value=gcip_tenant_id
            )
        )
        print(f"Atributo tenant_id actualizado a {gcip_tenant_id} para el usuario {looker_user_id}")

        # 3. Ejecutar Impersonación (Flujo Sudo)
        # El endpoint login_user devuelve un token específico para este usuario
        sudo_token = sdk.login_user(looker_user_id)
        print(" Token Sudo generado exitosamente.")

        # Devuelve el token (string) para que tu proxy lo inyecte en las cabeceras de las peticiones
        return sudo_token.access_token

    except looker_sdk.error.SDKError as e:
        print(f" Error en la API de Looker: {e}")
        raise

# --- Ejemplo de uso en tu endpoint del Proxy ---
# Datos extraídos del token de GCIP ya validado
usuario_email = "usuario.demo@empresa.com"
id_del_tenant_gcip = "tenant_xyz_889"
ID_DEL_ATRIBUTO_EN_LOOKER = 12 # Este ID lo obtienes de la configuración de Looker

try:
    # Obtener el token Sudo
    user_access_token = get_looker_sudo_token(
        gcip_email=usuario_email,
        gcip_tenant_id=id_del_tenant_gcip,
        tenant_attribute_id=ID_DEL_ATRIBUTO_EN_LOOKER
    )
   
    # Tu proxy ahora usa este 'user_access_token' como Bearer Token
    # para hacer las peticiones reales a la API de Looker a nombre del usuario.
    # Ejemplo de cabecera que armaría el proxy:
    # headers = {"Authorization": f"Bearer {user_access_token}"}

except Exception as err:
    print("Fallo en la autorización:", err)
