{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "eric-oss-hello-world-python-app.name" -}}
  {{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create version as used by the chart label.
*/}}
{{- define "eric-oss-hello-world-python-app.chart" -}}
  {{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "eric-oss-hello-world-python-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "eric-oss-hello-world-python-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "eric-oss-hello-world-python-app.labels" }}
app.kubernetes.io/name: {{ include "eric-oss-hello-world-python-app.name" . }}
helm.sh/chart: {{ include "eric-oss-hello-world-python-app.chart" . }}
{{ include "eric-oss-hello-world-python-app.selectorLabels" . }}
app.kubernetes.io/version: {{ include "eric-oss-hello-world-python-app.version" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Create chart version as used by the chart label.
*/}}
{{- define "eric-oss-hello-world-python-app.version" -}}
{{- printf "%s" .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create image registry url
*/}}
{{- define "eric-oss-hello-world-python-app.registryUrl" -}}
    {{- $registryURL := "armdocker.rnd.ericsson.se" -}}
    {{-  if .Values.global -}}
        {{- if .Values.global.registry -}}
            {{- if .Values.global.registry.url -}}
                {{- $registryURL = .Values.global.registry.url -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}
    {{- if .Values.imageCredentials.registry -}}
        {{- if .Values.imageCredentials.registry.url -}}
            {{- $registryURL = .Values.imageCredentials.registry.url -}}
        {{- end -}}
    {{- end -}}
    {{- print $registryURL -}}
{{- end -}}


{{/*
Create image pull secrets for global (outside of scope)
*/}}
{{- define "eric-oss-hello-world-python-app.pullSecret.global" -}}
{{- $pullSecret := "" -}}
{{- if .Values.global -}}
  {{- if .Values.global.pullSecret -}}
    {{- $pullSecret = .Values.global.pullSecret -}}
  {{- end -}}
{{- end -}}
{{- print $pullSecret -}}
{{- end -}}

{{/*
Create image pull secret, service level parameter takes precedence
*/}}
{{- define "eric-oss-hello-world-python-app.pullSecret" -}}
{{- $pullSecret := (include "eric-oss-hello-world-python-app.pullSecret.global" . ) -}}
{{- if .Values.imageCredentials -}}
  {{- if .Values.imageCredentials.pullSecret -}}
    {{- $pullSecret = .Values.imageCredentials.pullSecret -}}
  {{- end -}}
{{- end -}}
{{- print $pullSecret -}}
{{- end -}}

{{/*
Define Image Pull Policy
*/}}
{{- define "eric-oss-hello-world-python-app.registryImagePullPolicy.global" -}}
    {{- $globalRegistryPullPolicy := "IfNotPresent" -}}
    {{- if .Values.global -}}
        {{- if .Values.global.registry -}}
            {{- if .Values.global.registry.imagePullPolicy -}}
                {{- $globalRegistryPullPolicy = .Values.global.registry.imagePullPolicy -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}
    {{- print $globalRegistryPullPolicy -}}
{{- end -}}

{{/*
Define Image Pull Policy, service level parameter takes precedence
*/}}
{{- define "eric-oss-hello-world-python-app.registryImagePullPolicy" -}}
    {{- $globalRegistryPullPolicy := (include "eric-oss-hello-world-python-app.registryImagePullPolicy.global" . ) -}}
    {{- if .Values.imageCredentials -}}
        {{- if .Values.imageCredentials.pullPolicy -}}
            {{- $globalRegistryPullPolicy = .Values.imageCredentials.pullPolicy -}}
        {{- end -}}
    {{- end -}}
    {{- print $globalRegistryPullPolicy -}}
{{- end -}}

{{/*
Create image pull secrets
*/}}
{{- define "eric-oss-hello-world-python-app.pullSecrets" -}}
  {{- $pullSecret := "" -}}
  {{- if .Values.global -}}
      {{- if .Values.global.pullSecret -}}
          {{- $pullSecret = .Values.global.pullSecret -}}
      {{- end -}}
  {{- end -}}
  {{- if .Values.imageCredentials -}}
      {{- if .Values.imageCredentials.pullSecret -}}
          {{- $pullSecret = .Values.imageCredentials.pullSecret -}}
      {{- end -}}
  {{- end -}}
  {{- print $pullSecret -}}
{{- end -}}

{{/*
Timezone variable
*/}}
{{- define "eric-oss-hello-world-python-app.timezone" -}}
{{- $timezone := "UTC" -}}
{{- if .Values.global  -}}
    {{- if .Values.global.timezone -}}
        {{- $timezone = .Values.global.timezone -}}
    {{- end -}}
{{- end -}}
{{- print $timezone | quote -}}
{{- end -}}

{{/*
Retrieve AppArmor profile value for the securityContext in Kubernetes >=1.30.0
*/}}
{{- define "eric-oss-hello-world-python-app.appArmorProfile.type" -}}
{{ .Values.appArmorProfile.type | default "RuntimeDefault" | quote }}
{{- end }}

{{/*
Retrieve AppArmor profile value as a string for container annotations in Kubernetes <1.30.0
*/}}
{{- define "eric-oss-hello-world-python-app.appArmorProfileAnnotation" }}
{{- if .Values.appArmorProfile -}}
  {{ if eq .Values.appArmorProfile.type "RuntimeDefault" -}}
    "runtime/default"
  {{ else -}}
    {{ .Values.appArmorProfile.type | quote }}
  {{- end }}
{{- else -}}
  "runtime/default"
{{- end }}
{{- end }}
 
{{/*
Seccomp profile section (DR-1123-128)
*/}}
{{- define "eric-oss-hello-world-python-app.seccomp-profile" }}
    {{- if .Values.seccompProfile }}
      {{- if .Values.seccompProfile.type }}
          {{- if eq .Values.seccompProfile.type "Localhost" }}
              {{- if .Values.seccompProfile.localhostProfile }}
seccompProfile:
  type: {{ .Values.seccompProfile.type }}
  localhostProfile: {{ .Values.seccompProfile.localhostProfile }}
            {{- end }}
          {{- else }}
seccompProfile:
  type: {{ .Values.seccompProfile.type }}
          {{- end }}
        {{- end }}
    {{- end }}
{{- end }}

{{/*
Create image repo path
*/}}
{{- define "eric-oss-hello-world-python-app.repoPath" -}}
{{- if .Values.imageCredentials.repoPath -}}
{{- print .Values.imageCredentials.repoPath "/" -}}
{{- end -}}
{{- end -}}


{{- define "eric-oss-hello-world-python-app.product-info" }}
ericsson.com/product-name: {{ (fromYaml (.Files.Get "eric-product-info.yaml")).productName | quote }}
ericsson.com/product-number: {{ (fromYaml (.Files.Get "eric-product-info.yaml")).productNumber | quote }}
ericsson.com/product-revision: {{regexReplaceAll "(.*)[+|-].*" .Chart.Version "${1}" | quote }}
{{- end}}


{{/* Jeager tracer configuration env
*/}}
{{- define "eric-oss-hello-world-python-app.jaegerEnv" }}
- name: JAEGER_AGENT_HOST
  value: {{ .Values.env.jaeger.agent.host | quote }}
- name: JAEGER_AGENT_PORT
  value: {{ .Values.env.jaeger.agent.port | quote }}
- name: JAEGER_SAMPLER_TYPE
  value: {{ .Values.env.jaeger.sampler.type | quote }}
- name: JAEGER_SAMPLER_PARAM
  value: {{ .Values.env.jaeger.sampler.param | quote }}
- name: JAEGER_SAMPER_REFRESH_INTERVAL
  value: {{ .Values.env.jaeger.sampler.refreshInterval | quote }}
- name: JAEGER_REPORTER_LOG_SPANS
  value: {{ .Values.env.jaeger.reporter.logSpans | quote }}
- name: JAEGER_DISABLED
  value: {{ .Values.env.jaeger.disabled | quote }}
- name: JAEGER_TAGS
  value: {{ .Values.env.jaeger.tags | quote }}
{{- end }}

{{/*
Create any image path from eric-product-info.yaml (DR-D1121-067)
*/}}
{{- define "eric-oss-hello-world-python-app.imagePath" }}
    {{- $imageId := index . "imageId" -}}
    {{- $values := index . "values" -}}
    {{- $files := index . "files" -}}
    {{- $productInfo := fromYaml ($files.Get "eric-product-info.yaml") -}}
    {{- $registryUrl := index $productInfo "images" $imageId "registry" -}}
    {{- $repoPath := index $productInfo "images" $imageId "repoPath" -}}
    {{- $name := index $productInfo "images" $imageId "name" -}}
    {{- $tag :=  index $productInfo "images" $imageId "tag" -}}
    {{- if $values.global -}}
        {{- if $values.global.registry -}}
            {{- $registryUrl = default $registryUrl $values.global.registry.url -}}
        {{- end -}}
    {{- end -}}
    {{- if $values.imageCredentials -}}
        {{- if $values.imageCredentials.registry -}}
            {{- $registryUrl = default $registryUrl $values.imageCredentials.registry.url -}}
        {{- end -}}
        {{- if not (kindIs "invalid" $values.imageCredentials.repoPath) -}}
            {{- $repoPath = $values.imageCredentials.repoPath -}}
        {{- end -}}
        {{- $image := index $values.imageCredentials $imageId -}}
        {{- if $image -}}
            {{- if $image.registry -}}
                {{- $registryUrl = default $registryUrl $image.registry.url -}}
            {{- end -}}
            {{- if not (kindIs "invalid" $image.repoPath) -}}
                {{- $repoPath = $image.repoPath -}}
            {{- end -}}
        {{- end -}}
    {{- end -}}
    {{- if $repoPath -}}
        {{- $repoPath = printf "%s/" $repoPath -}}
    {{- end -}}
    {{- printf "%s/%s%s:%s" $registryUrl $repoPath $name $tag -}}
{{- end -}}

{{/*
Create a merged set of nodeSelectors from global and service level.
*/}}
{{- define "eric-oss-hello-world-python-app.nodeSelector" -}}
{{- $globalValue := (dict) -}}
{{- if .Values.global -}}
    {{- if .Values.global.nodeSelector -}}
      {{- $globalValue = .Values.global.nodeSelector -}}
    {{- end -}}
{{- end -}}
{{- if .Values.nodeSelector -}}
  {{- range $key, $localValue := .Values.nodeSelector -}}
    {{- if hasKey $globalValue $key -}}
         {{- $Value := index $globalValue $key -}}
         {{- if ne $Value $localValue -}}
           {{- printf "nodeSelector \"%s\" is specified in both global (%s: %s) and service level (%s: %s) with differing values which is not allowed." $key $key $globalValue $key $localValue | fail -}}
         {{- end -}}
     {{- end -}}
    {{- end -}}
    {{- toYaml (merge $globalValue .Values.nodeSelector) | trim | indent 2 -}}
{{- else -}}
  {{- if not ( empty $globalValue ) -}}
    {{- toYaml $globalValue | trim | indent 2 -}}
  {{- end -}}
{{- end -}}
{{- end -}}

{{- define "eric-oss-hello-world-python-app.tolerations" -}}
{{- if .Values.tolerations -}}
  {{- toYaml .Values.tolerations -}}
{{- end -}}
{{- end -}}

{{/*
Define upper limit for TerminationGracePeriodSeconds
*/}}
{{- define "eric-oss-hello-world-python-app.terminationGracePeriodSeconds" -}}
{{- if .Values.terminationGracePeriodSeconds -}}
  {{- toYaml .Values.terminationGracePeriodSeconds -}}
{{- end -}}
{{- end -}}

{{/*
Define the role reference for security policy
*/}}
{{- define "eric-oss-hello-world-python-app.securityPolicy.reference" -}}
  {{- if .Values.global -}}
    {{- if .Values.global.security -}}
      {{- if .Values.global.security.policyReferenceMap -}}
        {{ $mapped := index .Values "global" "security" "policyReferenceMap" "default-restricted-security-policy" }}
        {{- if $mapped -}}
          {{ $mapped }}
        {{- else -}}
          default-restricted-security-policy
        {{- end -}}
      {{- else -}}
        default-restricted-security-policy
      {{- end -}}
    {{- else -}}
      default-restricted-security-policy
    {{- end -}}
  {{- else -}}
    default-restricted-security-policy
  {{- end -}}
{{- end -}}

{{/*
Define the annotations for security policy
*/}}
{{- define "eric-oss-hello-world-python-app.securityPolicy.annotations" -}}
# Automatically generated annotations for documentation purposes.
{{- end -}}

{{/*
Define the function to get the secret name
 */}}
{{- define "eric-oss-hello-world-python-app.clientSecret" -}}
{{- $clientSecret := "" -}}
{{- if .Values.global }}
  {{- if .Values.global.clientCredentials }}
    {{- if .Values.global.clientCredentials.secret }}
      {{- if .Values.global.clientCredentials.secret.name }}
        {{- $clientSecret = .Values.global.clientCredentials.secret.name }}
      {{- end }}
    {{- end }}
  {{- end }}
{{- end }}
{{- print $clientSecret }}
{{- end }}
