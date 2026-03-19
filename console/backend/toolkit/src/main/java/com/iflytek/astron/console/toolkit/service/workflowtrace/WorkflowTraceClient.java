package com.iflytek.astron.console.toolkit.service.workflowtrace;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.toolkit.config.properties.ApiUrl;
import com.iflytek.astron.console.toolkit.entity.core.workflowtrace.WorkflowTraceExecutionDetailDto;
import com.iflytek.astron.console.toolkit.entity.core.workflowtrace.WorkflowTraceExecutionPageDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

@Slf4j
@Service
@RequiredArgsConstructor
public class WorkflowTraceClient {

    private static final String EXECUTIONS_PATH = "/workflow-trace/v1/executions";

    private final ApiUrl apiUrl;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public WorkflowTraceExecutionPageDto queryExecutions(
            String flowId,
            @Nullable String appId,
            @Nullable String chatId,
            @Nullable Long startTime,
            @Nullable Long endTime,
            Integer page,
            Integer pageSize,
            HttpHeaders inboundHeaders) {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("flow_id", flowId);
        addIfPresent(params, "app_id", appId);
        addIfPresent(params, "chat_id", chatId);
        addIfPresent(params, "start_time", startTime);
        addIfPresent(params, "end_time", endTime);
        addIfPresent(params, "page", page);
        addIfPresent(params, "page_size", pageSize);

        JsonNode data = exchange(EXECUTIONS_PATH, params, inboundHeaders);
        try {
            return objectMapper.treeToValue(data, WorkflowTraceExecutionPageDto.class);
        } catch (JsonProcessingException e) {
            log.error("Failed to deserialize workflow trace execution page, flowId={}", flowId, e);
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace page deserialize failed");
        }
    }

    public WorkflowTraceExecutionDetailDto getExecutionDetail(
            String sid,
            String flowId,
            @Nullable String appId,
            HttpHeaders inboundHeaders) {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        params.add("flow_id", flowId);
        addIfPresent(params, "app_id", appId);

        JsonNode data = exchange(EXECUTIONS_PATH + "/" + sid, params, inboundHeaders);
        try {
            return objectMapper.treeToValue(data, WorkflowTraceExecutionDetailDto.class);
        } catch (JsonProcessingException e) {
            log.error("Failed to deserialize workflow trace execution detail, sid={}, flowId={}", sid, flowId, e);
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace detail deserialize failed");
        }
    }

    private JsonNode exchange(
            String path,
            MultiValueMap<String, String> params,
            HttpHeaders inboundHeaders) {
        String url = UriComponentsBuilder.fromHttpUrl(apiUrl.getWorkflowTrace().concat(path))
                .queryParams(params)
                .build()
                .toUriString();
        HttpEntity<Void> entity = new HttpEntity<>(buildHeaders(inboundHeaders));
        ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);

        if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace request failed");
        }

        try {
            JsonNode root = objectMapper.readTree(response.getBody());
            int code = root.path("code").asInt(-1);
            if (code != 0) {
                throw new BusinessException(ResponseEnum.RESPONSE_FAILED, root.path("message").asText("workflow trace request failed"));
            }
            return root.path("data");
        } catch (JsonProcessingException e) {
            log.error("Failed to parse workflow trace response: {}", response.getBody(), e);
            throw new BusinessException(ResponseEnum.RESPONSE_FAILED, "workflow trace response parse failed");
        }
    }

    private HttpHeaders buildHeaders(HttpHeaders inboundHeaders) {
        HttpHeaders headers = new HttpHeaders();
        copyIfPresent(inboundHeaders, headers, HttpHeaders.AUTHORIZATION);
        copyIfPresent(inboundHeaders, headers, "space-id");
        copyIfPresent(inboundHeaders, headers, "enterprise-id");
        copyIfPresent(inboundHeaders, headers, HttpHeaders.ACCEPT_LANGUAGE);
        copyIfPresent(inboundHeaders, headers, "x-request-id");
        copyIfPresent(inboundHeaders, headers, "x-user-id");
        return headers;
    }

    private void copyIfPresent(HttpHeaders source, HttpHeaders target, String name) {
        if (source.containsKey(name)) {
            target.put(name, source.get(name));
        }
    }

    private void addIfPresent(MultiValueMap<String, String> params, String name, @Nullable Object value) {
        if (value != null) {
            params.add(name, String.valueOf(value));
        }
    }
}
