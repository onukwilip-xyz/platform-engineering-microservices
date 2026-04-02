
# ---- Build stage ----
FROM gradle:7.5-jdk17-alpine AS builder
WORKDIR /app
COPY build.gradle .
COPY settings.gradle .
RUN gradle dependencies --no-daemon
COPY src src
RUN gradle build -x test --no-daemon

# ---- Runtime stage ----
FROM eclipse-temurin:17-jre-alpine
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring
COPY --from=builder /app/build/libs/cart-1.0.0.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]