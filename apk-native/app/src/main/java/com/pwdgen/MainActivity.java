package com.pwdgen;

import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.pwdgen.app.R;

public class MainActivity extends AppCompatActivity {

    private EditText inputText;
    private EditText lengthText;
    private CheckBox chkUpper;
    private CheckBox chkSymbol;
    private CheckBox chkLegacy;
    private TextView outputText;
    private View btnCopy;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);

        // Edge-to-edge insets
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(android.R.id.content), (v, insets) -> {
            int top = insets.getInsets(WindowInsetsCompat.Type.systemBars()).top;
            v.setPadding(v.getPaddingLeft(), top, v.getPaddingRight(), v.getPaddingBottom());
            return insets;
        });

        // Find views
        inputText = findViewById(R.id.inputText);
        lengthText = findViewById(R.id.lengthText);
        chkUpper = findViewById(R.id.chkUpper);
        chkSymbol = findViewById(R.id.chkSymbol);
        chkLegacy = findViewById(R.id.chkLegacy);
        outputText = findViewById(R.id.outputText);
        btnCopy = findViewById(R.id.btnCopy);

        // Generate button
        findViewById(R.id.btnGenerate).setOnClickListener(v -> {
            String input = inputText.getText().toString().trim();
            if (input.isEmpty()) {
                Toast.makeText(this, "请填写输入信息", Toast.LENGTH_SHORT).show();
                return;
            }

            int length;
            try {
                length = Integer.parseInt(lengthText.getText().toString().trim());
            } catch (NumberFormatException e) {
                length = 15;
                lengthText.setText("15");
            }

            String password;
            if (chkLegacy.isChecked()) {
                password = PasswordGenerator.generateLegacy(
                    input, length, chkUpper.isChecked(), chkSymbol.isChecked()
                );
            } else {
                password = PasswordGenerator.generate(
                    input, length, chkUpper.isChecked(), chkSymbol.isChecked()
                );
            }

            outputText.setText(password);
            outputText.setTextColor(getColor(R.color.text_primary));
            outputText.setTextSize(18);
            btnCopy.setVisibility(View.VISIBLE);
        });

        // Status bar: light background -> dark icons
        Window window = getWindow();
        WindowCompat.getInsetsController(window, window.getDecorView())
            .setAppearanceLightStatusBars(true);

        // Help button
        findViewById(R.id.btnHelp).setOnClickListener(v -> showHelp());

        // GitHub button
        findViewById(R.id.btnGitHub).setOnClickListener(v -> {
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/l3174"));
            startActivity(intent);
        });

        // Copy button
        btnCopy.setOnClickListener(v -> {
            String text = outputText.getText().toString();
            ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            clipboard.setPrimaryClip(ClipData.newPlainText("password", text));
            Toast.makeText(this, "已复制到剪贴板", Toast.LENGTH_SHORT).show();
        });
    }

    private void showHelp() {
        String msg = "这是一个确定性密码生成器——不存储密码，而是通过加密算法从你输入的信息中派生出密码。\n\n" +
            "━━ 使用方法 ━━\n\n" +
            "1. 在「输入信息」中填入你的主密码和标识\n" +
            "   如：MySecret123+github\n" +
            "2. 设置密码长度，建议 12–16 位\n" +
            "3. 根据需要勾选「包含大写字母」和「包含特殊符号」\n" +
            "4. 点击「生成密码」得到结果，点击「复制到剪贴板」使用\n\n" +
            "━━ 加密规则 ━━\n\n" +
            "SHA-256 哈希\n" +
            "对输入信息进行 SHA-256 哈希，相同输入永远产生相同哈希，保证同一输入 + 相同设置 = 永远一样的密码。\n\n" +
            "字符集映射\n" +
            "将每个哈希字节（0–255）对字符集大小取模，映射到可打印字符。需要更多字符时通过追加计数器反复哈希扩展。\n\n" +
            "类别锚点\n" +
            "勾选的每类字符各取一个锚点，确保结果中每类至少出现一次（小写字母+数字始终包含）。\n\n" +
            "Fisher-Yates 洗牌\n" +
            "用哈希导出的序列做确定性洗牌，打散锚点位置，使密码看起来完全随机。\n\n" +
            "━━ 传统模式 ━━\n\n" +
            "勾选「传统模式」后，密码直接从 SHA-256 的十六进制串截取（如 3056fe9a...），大写和符号选项改为修改这个 hex 字符串。\n\n" +
            "好处：即使脱离本工具，在任何 SHA-256 在线生成网站输入相同信息，也能手动找回密码，永远不会被工具锁死。\n\n" +
            "代价：hex 直取的字符空间只有 16 个（0-9, a-f），安全性远不如字符集映射模式。建议一般用户不勾选，仅在需要跨工具兼容时使用。\n\n" +
            "━━ 安全建议 ━━\n\n" +
            "· 输入信息中应包含足够长的主密码，仅你一人知晓\n" +
            "· 不同网站使用不同标识（如 +github、+google）\n" +
            "· 勿将主密码明文保存或与他人分享";

        new AlertDialog.Builder(this)
            .setTitle("使用说明")
            .setMessage(msg)
            .setPositiveButton("关闭", null)
            .show();
    }
}
