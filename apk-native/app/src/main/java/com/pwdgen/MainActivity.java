package com.pwdgen;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.pwdgen.app.R;

public class MainActivity extends AppCompatActivity {

    private EditText inputText;
    private EditText lengthText;
    private CheckBox chkUpper;
    private CheckBox chkSymbol;
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
                length = 12;
                lengthText.setText("12");
            }

            String password = PasswordGenerator.generate(
                input, length, chkUpper.isChecked(), chkSymbol.isChecked()
            );

            outputText.setText(password);
            outputText.setTextColor(getColor(R.color.text_primary));
            outputText.setTextSize(18);
            btnCopy.setVisibility(View.VISIBLE);
        });

        // Copy button
        btnCopy.setOnClickListener(v -> {
            String text = outputText.getText().toString();
            ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            clipboard.setPrimaryClip(ClipData.newPlainText("password", text));
            Toast.makeText(this, "已复制到剪贴板", Toast.LENGTH_SHORT).show();
        });
    }
}
