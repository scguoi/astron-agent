package com.iflytek.astron.console.toolkit.service.workflowtrace;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.toolkit.config.properties.WorkflowTraceProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.Credentials;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;
import java.io.IOException;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
@RequiredArgsConstructor
public class WorkflowTraceEsClient {

    private static final MediaType JSON_MEDIA_TYPE = MediaType.get("application/json; charset=utf-8");

    private final WorkflowTraceProperties workflowTraceProperties;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private volatile OkHttpClient verifiedClient;
    private volatile OkHttpClient insecureClient;

    public JsonNode search(JsonNode body) {
        Request.Builder requestBuilder = new Request.Builder()
                .url(buildSearchUrl())
                .post(RequestBody.create(body.toString(), JSON_MEDIA_TYPE));
        if (StringUtils.isNotBlank(workflowTraceProperties.getEsUsername())) {
            requestBuilder.header(
                    "Authorization",
                    Credentials.basic(
                            workflowTraceProperties.getEsUsername(),
                            StringUtils.defaultString(workflowTraceProperties.getEsPassword())));
        }

        try (Response response = getClient().newCall(requestBuilder.build()).execute()) {
            if (!response.isSuccessful() || response.body() == null) {
                String errorBody = response.body() == null ? "" : response.body().string();
                log.error("Workflow trace search failed, code={}, body={}", response.code(), errorBody);
                throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace request failed");
            }
            return objectMapper.readTree(response.body().string());
        } catch (JsonProcessingException e) {
            log.error("Failed to parse workflow trace response", e);
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace response parse failed");
        } catch (IOException e) {
            log.error("Workflow trace search request failed", e);
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace request failed");
        }
    }

    private String buildSearchUrl() {
        return StringUtils.removeEnd(workflowTraceProperties.getEsUrl(), "/")
                + "/"
                + workflowTraceProperties.getEsIndex()
                + "/_search";
    }

    private OkHttpClient getClient() {
        if (workflowTraceProperties.isEsVerify()) {
            if (verifiedClient == null) {
                synchronized (this) {
                    if (verifiedClient == null) {
                        verifiedClient = buildClient(true);
                    }
                }
            }
            return verifiedClient;
        }

        if (insecureClient == null) {
            synchronized (this) {
                if (insecureClient == null) {
                    insecureClient = buildClient(false);
                }
            }
        }
        return insecureClient;
    }

    private OkHttpClient buildClient(boolean verifySsl) {
        OkHttpClient.Builder builder = new OkHttpClient.Builder()
                .connectTimeout(workflowTraceProperties.getEsTimeoutSeconds(), TimeUnit.SECONDS)
                .readTimeout(workflowTraceProperties.getEsTimeoutSeconds(), TimeUnit.SECONDS)
                .writeTimeout(workflowTraceProperties.getEsTimeoutSeconds(), TimeUnit.SECONDS)
                .callTimeout(workflowTraceProperties.getEsTimeoutSeconds(), TimeUnit.SECONDS);
        if (!verifySsl) {
            X509TrustManager trustManager = buildTrustAllManager();
            SSLSocketFactory socketFactory = buildTrustAllSocketFactory(trustManager);
            builder.sslSocketFactory(socketFactory, trustManager);
            builder.hostnameVerifier(new TrustAllHostnameVerifier());
        }
        return builder.build();
    }

    private X509TrustManager buildTrustAllManager() {
        return new X509TrustManager() {
            @Override
            public void checkClientTrusted(X509Certificate[] chain, String authType) {}

            @Override
            public void checkServerTrusted(X509Certificate[] chain, String authType) {}

            @Override
            public X509Certificate[] getAcceptedIssuers() {
                return new X509Certificate[0];
            }
        };
    }

    private SSLSocketFactory buildTrustAllSocketFactory(X509TrustManager trustManager) {
        try {
            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(null, new TrustManager[] {trustManager}, new SecureRandom());
            return sslContext.getSocketFactory();
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("Failed to initialize insecure SSL context for workflow trace", e);
        }
    }

    private static final class TrustAllHostnameVerifier implements HostnameVerifier {
        @Override
        public boolean verify(String hostname, SSLSession session) {
            return true;
        }
    }
}
