package dev.adaptive

import org.jetbrains.kotlin.com.intellij.openapi.util.Disposer
import org.jetbrains.kotlin.cli.common.CLIConfigurationKeys
import org.jetbrains.kotlin.cli.common.messages.MessageCollector
import org.jetbrains.kotlin.cli.jvm.compiler.EnvironmentConfigFiles
import org.jetbrains.kotlin.cli.jvm.compiler.KotlinCoreEnvironment
import org.jetbrains.kotlin.config.CommonConfigurationKeys
import org.jetbrains.kotlin.config.CompilerConfiguration
import org.jetbrains.kotlin.psi.KtAnnotationEntry
import org.jetbrains.kotlin.psi.KtCallExpression
import org.jetbrains.kotlin.psi.KtFile
import org.jetbrains.kotlin.psi.KtLambdaExpression
import org.jetbrains.kotlin.psi.KtPsiFactory
import org.jetbrains.kotlin.psi.psiUtil.collectDescendantsOfType
import java.io.File

private const val ITEM_THRESHOLD = 5

private data class Finding(
    val severity: String,
    val category: String,
    val file: String,
    val line: Int,
    val message: String,
    val fix: String,
)

private data class Args(
    val src: List<String>,
    val format: String,
)

fun main(rawArgs: Array<String>) {
    val args = parseArgs(rawArgs)
    val ktFiles = collectKotlinFiles(args.src)

    val findings = mutableListOf<Finding>()
    val disposable = Disposer.newDisposable()

    try {
        val configuration = CompilerConfiguration().apply {
            put(CommonConfigurationKeys.MODULE_NAME, "psi-audit")
            put(CLIConfigurationKeys.MESSAGE_COLLECTOR_KEY, MessageCollector.NONE)
        }
        val environment = KotlinCoreEnvironment.createForProduction(
            disposable,
            configuration,
            EnvironmentConfigFiles.JVM_CONFIG_FILES,
        )
        val psiFactory = KtPsiFactory(environment.project, false)

        ktFiles.forEach { file ->
            val content = file.readText()
            val ktFile = psiFactory.createFile(file.name, content)
            findings += checkDeprecatedWindowSizeApi(file, content, ktFile)
            findings += checkMissingOptIn(file, content, ktFile)
            findings += checkTextOverflow(file, content, ktFile)
            findings += checkScrollability(file, content, ktFile)
        }

        if (args.format == "json") {
            println(formatJson(ktFiles.size, findings))
        } else {
            println(formatText(ktFiles.size, findings))
        }

        val criticalCount = findings.count { it.severity == "CRITICAL" }
        kotlin.system.exitProcess(if (criticalCount > 0) 1 else 0)
    } finally {
        Disposer.dispose(disposable)
    }
}

private fun parseArgs(rawArgs: Array<String>): Args {
    if (rawArgs.isEmpty()) {
        printUsageAndExit()
    }

    val src = mutableListOf<String>()
    var format = "text"
    var i = 0
    while (i < rawArgs.size) {
        when (val arg = rawArgs[i]) {
            "--src" -> {
                i++
                while (i < rawArgs.size && !rawArgs[i].startsWith("--")) {
                    src += rawArgs[i]
                    i++
                }
                continue
            }
            "--format" -> {
                i++
                if (i >= rawArgs.size) printUsageAndExit()
                format = rawArgs[i]
            }
            else -> {
                if (arg.startsWith("--")) {
                    printUsageAndExit("Unknown arg: $arg")
                }
            }
        }
        i++
    }

    if (src.isEmpty()) {
        printUsageAndExit("Missing --src")
    }
    if (format !in setOf("text", "json")) {
        printUsageAndExit("Invalid --format: $format")
    }
    return Args(src = src, format = format)
}

private fun printUsageAndExit(message: String? = null): Nothing {
    if (message != null) {
        System.err.println(message)
    }
    System.err.println("Usage: psi-audit --src <path ...> [--format text|json]")
    kotlin.system.exitProcess(2)
}

private fun collectKotlinFiles(targets: List<String>): List<File> {
    val files = mutableSetOf<File>()
    targets.forEach { target ->
        val f = File(target)
        if (!f.exists()) return@forEach
        if (f.isFile && f.extension == "kt") {
            files += f.absoluteFile
        } else if (f.isDirectory) {
            f.walkTopDown()
                .onEnter { dir -> dir.name !in setOf("build", ".gradle", ".git", "node_modules") }
                .filter { it.isFile && it.extension == "kt" }
                .forEach { files += it.absoluteFile }
        }
    }
    return files.sortedBy { it.path }
}

private fun checkDeprecatedWindowSizeApi(file: File, content: String, ktFile: KtFile): List<Finding> {
    val out = mutableListOf<Finding>()
    ktFile.collectDescendantsOfType<KtCallExpression>().forEach { call ->
        val callee = call.calleeExpression?.text ?: return@forEach
        if (callee == "calculateWindowSizeClass") {
            out += Finding(
                severity = "CRITICAL",
                category = "WindowSizeClass",
                file = file.path,
                line = lineNumber(content, call.textOffset),
                message = "calculateWindowSizeClass() is deprecated.",
                fix = "Use currentWindowAdaptiveInfo().windowSizeClass",
            )
        }
    }
    return out
}

private fun checkMissingOptIn(file: File, content: String, ktFile: KtFile): List<Finding> {
    val adaptiveCalls = setOf(
        "ListDetailPaneScaffold",
        "SupportingPaneScaffold",
        "NavigableListDetailPaneScaffold",
        "NavigableSupportingPaneScaffold",
        "AdaptiveNavigationSuite",
        "currentWindowAdaptiveInfo",
    )

    val usesAdaptiveApi = ktFile.collectDescendantsOfType<KtCallExpression>()
        .any { (it.calleeExpression?.text ?: "") in adaptiveCalls }

    if (!usesAdaptiveApi) return emptyList()

    val hasOptIn = ktFile.collectDescendantsOfType<KtAnnotationEntry>().any { ann ->
        val text = ann.text
        text.contains("OptIn(") && text.contains("ExperimentalMaterial3AdaptiveApi::class")
    }

    if (hasOptIn) return emptyList()

    return listOf(
        Finding(
            severity = "CRITICAL",
            category = "WindowSizeClass",
            file = file.path,
            line = 1,
            message = "Adaptive scaffold APIs used without @OptIn(ExperimentalMaterial3AdaptiveApi::class).",
            fix = "Add @file:OptIn(ExperimentalMaterial3AdaptiveApi::class)",
        )
    )
}

private fun checkTextOverflow(file: File, content: String, ktFile: KtFile): List<Finding> {
    val out = mutableListOf<Finding>()
    ktFile.collectDescendantsOfType<KtCallExpression>().forEach { call ->
        val callee = call.calleeExpression?.text ?: return@forEach
        if (callee != "Text") return@forEach

        val args = call.valueArguments.mapNotNull { it.getArgumentName()?.asName?.identifier }
        val hasOverflow = args.contains("overflow")
        val hasMaxLines = args.contains("maxLines")

        if (!hasOverflow && !hasMaxLines) {
            out += Finding(
                severity = "INFO",
                category = "TextOverflow",
                file = file.path,
                line = lineNumber(content, call.textOffset),
                message = "Text() without overflow/maxLines — clips unpredictably on small screens.",
                fix = "Add maxLines and overflow for constrained text.",
            )
        }
    }
    return out
}

private fun checkScrollability(file: File, content: String, ktFile: KtFile): List<Finding> {
    val out = mutableListOf<Finding>()
    ktFile.collectDescendantsOfType<KtCallExpression>().forEach { call ->
        val callee = call.calleeExpression?.text ?: return@forEach
        if (callee != "Column") return@forEach

        val hasVerticalScroll = call.text.contains("verticalScroll(")
        val lambda = extractLambda(call) ?: return@forEach
        val signalCount = lambda.collectDescendantsOfType<KtCallExpression>().count {
            (it.calleeExpression?.text ?: "") in setOf("Text", "Button", "item")
        }

        if (signalCount >= ITEM_THRESHOLD && !hasVerticalScroll) {
            out += Finding(
                severity = "WARNING",
                category = "Scrollability",
                file = file.path,
                line = lineNumber(content, call.textOffset),
                message = "Column with ~$signalCount child signals has no verticalScroll modifier.",
                fix = "Add Modifier.verticalScroll(...) or use LazyColumn.",
            )
        }
    }
    return out
}

private fun extractLambda(call: KtCallExpression): KtLambdaExpression? {
    call.lambdaArguments.firstOrNull()?.getLambdaExpression()?.let { return it }
    val argExpr = call.valueArguments
        .firstOrNull { it.getArgumentExpression() is KtLambdaExpression }
        ?.getArgumentExpression()
    return argExpr as? KtLambdaExpression
}

private fun lineNumber(content: String, offset: Int): Int {
    if (offset <= 0) return 1
    return content.take(offset).count { it == '\n' } + 1
}

private fun formatText(scannedKt: Int, findings: List<Finding>): String {
    val critical = findings.count { it.severity == "CRITICAL" }
    val warning = findings.count { it.severity == "WARNING" }
    val info = findings.count { it.severity == "INFO" }

    val header = buildString {
        appendLine("PSI AUDIT")
        appendLine("Scanned: $scannedKt kt")
        appendLine("Findings: $critical CRITICAL · $warning WARNING · $info INFO")
    }

    if (findings.isEmpty()) return header

    val body = findings.joinToString("\n") { f ->
        "[${f.severity}] ${File(f.file).name}:${f.line} ${f.category} - ${f.message}"
    }
    return "$header\n$body"
}

private fun formatJson(scannedKt: Int, findings: List<Finding>): String {
    val critical = findings.count { it.severity == "CRITICAL" }
    val warning = findings.count { it.severity == "WARNING" }
    val info = findings.count { it.severity == "INFO" }

    val findingJson = findings.joinToString(",\n") { f ->
        """
    {
      "severity": "${escapeJson(f.severity)}",
      "category": "${escapeJson(f.category)}",
      "file": "${escapeJson(f.file)}",
      "line": ${f.line},
      "message": "${escapeJson(f.message)}",
      "fix": "${escapeJson(f.fix)}"
    }
        """.trimIndent()
    }

    return """
{
  "scanned_kt": $scannedKt,
  "summary": {
    "critical": $critical,
    "warning": $warning,
    "info": $info
  },
  "findings": [
$findingJson
  ]
}
    """.trimIndent()
}

private fun escapeJson(value: String): String {
    return value
        .replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
}
