# scripts/setup-ssl.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    [string]$Email="admin@$Domain"
)

Write-Host "🌐 Подготовка SSL для: $Domain" -ForegroundColor Cyan

# 1. Останавливаем стек, чтобы освободить 80 порт для Certbot
docker compose -f docker-compose.prod.yml down

# 2. Запускаем Certbot в режиме webroot (получает сертификат без остановки Nginx в будущем)
docker run --rm -it `
  -v "${PWD}/certbot/conf:/etc/letsencrypt" `
  -v "${PWD}/certbot/www:/var/www/certbot" `
  certbot/certbot certonly --webroot -w /var/www/certbot `
  --email $Email --agree-tos --no-eff-email -d $Domain

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Сертификат успешно получен!" -ForegroundColor Green
    Write-Host "🚀 Запускаем production-стек с HTTPS..." -ForegroundColor Cyan
    docker compose -f docker-compose.prod.yml up -d
} else {
    Write-Host "❌ Ошибка получения сертификата. Проверьте, что домен указывает на IP сервера." -ForegroundColor Red
}