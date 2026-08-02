# Operación — que la app no se muera en silencio

> Escrito el 2026-08-02, después de descubrir que el backend llevaba **siete
> semanas caído** sin que nadie lo supiera.

## Qué pasó

El trial de Railway ($5, 30 días) venció alrededor del 16 de junio. Railway
eliminó el servicio. El frontend en Vercel siguió vivo — es estático, no se
cae — apuntando a un backend que ya no existía.

Resultado: una clienta escaneaba el QR de su mesa, la página cargaba, y el menú
nunca aparecía. Nadie se enteró porque **nada estaba vigilando**.

`docs/hosting-and-costs.md` ya lo había previsto en junio: *"cuando se acabe el
trial, pasar Railway a Hobby (~$5/mes)"*. Ese paso nunca se dio.

## Las dos protecciones que ahora existen

### 1. Vigilante de disponibilidad — `.github/workflows/uptime.yml`

Cada 15 minutos golpea `/health` del backend y la portada del frontend. Si algo
no responde, la acción **falla**, y GitHub le manda un correo a la dueña del
repositorio. Eso es la alerta: sin servicios de terceros y sin costo.

`/health` **consulta la base de datos** a propósito. Una revisión que sólo
comprobara que el proceso vive habría reportado esta app como sana durante todo
el apagón, porque Postgres puede estar caído mientras FastAPI responde feliz.

**Hay que configurar dos variables** en *Settings → Secrets and variables →
Actions → Variables*:

| Variable | Valor |
|---|---|
| `BACKEND_URL` | la URL del backend, sin barra final |
| `FRONTEND_URL` | la URL del frontend |

⚠️ GitHub **desactiva las acciones programadas tras 60 días sin actividad** en
el repositorio. Si el proyecto se queda quieto, hay que volver a activarlas
desde la pestaña Actions.

### 2. Respaldo cifrado — `.github/workflows/backup.yml`

Cada noche a las 3:00 de Colombia hace un `pg_dump` y lo guarda 30 días.

**Va cifrado porque este repositorio es público** y los archivos generados por
las acciones se pueden descargar libremente. Un volcado sin cifrar publicaría
los pedidos de clientes reales. Si falta la contraseña, el trabajo **se niega a
correr** en vez de publicar datos.

**Hay que configurar dos secretos** en *Settings → Secrets and variables →
Actions → Secrets*:

| Secreto | Valor |
|---|---|
| `DATABASE_URL` | la cadena de conexión de Postgres en Railway |
| `BACKUP_PASSPHRASE` | una contraseña larga, guardada donde no se pierda |

Para recuperar un respaldo:

```bash
gpg --decrypt madre-mia-2026-08-02.sql.gpg > dump.sql
psql "$DATABASE_URL" < dump.sql
```

> Si se pierde la contraseña, los respaldos son irrecuperables. Guárdala en el
> mismo sitio donde guardas la del admin.

## Lo que sigue faltando

- **Pasar Railway a Hobby ($5/mes).** Mientras siga en trial, esto se repite.
- **Confirmar si la base de datos sobrevivió** al borrado del servicio.
