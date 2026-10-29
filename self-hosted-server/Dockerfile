# =========================================================================
# DOCKERFILE CHO SELF-HOSTED WEB API (NT106 - LẬP TRÌNH MẠNG CĂN BẢN)
# Hỗ trợ tự động build và deploy trên Render, Railway, Fly.io, VPS Docker
# =========================================================================

# GIAI ĐOẠN 1: BUILD VÀ BIÊN DỊCH CODE (Sử dụng .NET 10 SDK)
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Copy file .csproj trước để tận dụng Docker Cache layer khi restore package
COPY self-hosted-server.csproj ./
RUN dotnet restore self-hosted-server.csproj

# Copy toàn bộ mã nguồn còn lại
COPY . ./

# Biên dịch ứng dụng ra file binary tối ưu cho môi trường Release
RUN dotnet publish self-hosted-server.csproj -c Release -o /app/publish /p:UseAppHost=false

# GIAI ĐOẠN 2: RUNTIME CHẠY ỨNG DỤNG (Chỉ chứa Runtime siêu nhẹ, tối ưu RAM)
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app

# Copy các file đã biên dịch từ giai đoạn build sang
COPY --from=build /app/publish .

# Thiết lập biến môi trường mặc định (Render/Railway sẽ tự động ghi đè PORT)
ENV ASPNETCORE_ENVIRONMENT=Production
ENV PORT=8080

# Expose cổng kết nối mạng
EXPOSE 8080

# Lệnh khởi chạy ứng dụng
ENTRYPOINT ["dotnet", "self-hosted-server.dll"]
