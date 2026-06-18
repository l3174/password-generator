package com.pwdgen;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;

public class PasswordGenerator {

    public static final String LOWERCASE = "abcdefghijkmnopqrstuvwxyz";
    public static final String UPPERCASE = "ABCDEFGHJKLMNPQRSTUVWXYZ";
    public static final String DIGITS = "23456789";
    public static final String SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?";

    public static String generate(String input, int length, boolean includeUpper, boolean includeSymbols) {
        List<String> categories = new ArrayList<>();
        categories.add(LOWERCASE);
        categories.add(DIGITS);
        if (includeUpper) categories.add(UPPERCASE);
        if (includeSymbols) categories.add(SYMBOLS);

        StringBuilder fullCharset = new StringBuilder();
        for (String cat : categories) fullCharset.append(cat);

        int catCount = categories.size();
        if (length < catCount) length = catCount;

        byte[] raw = expandBytes(input, length * 3);

        // Anchor chars - one from each category
        List<Character> chars = new ArrayList<>();
        for (int i = 0; i < catCount; i++) {
            String cat = categories.get(i);
            chars.add(cat.charAt((raw[i] & 0xFF) % cat.length()));
        }

        // Fill remaining from full charset
        for (int i = 0; i < length - catCount; i++) {
            int idx = (raw[catCount + i] & 0xFF) % fullCharset.length();
            chars.add(fullCharset.charAt(idx));
        }

        // Deterministic Fisher-Yates shuffle
        byte[] shuffleBytes = new byte[length * 2];
        System.arraycopy(raw, length, shuffleBytes, 0, Math.min(shuffleBytes.length, raw.length - length));
        int shuffleIdx = 0;

        for (int i = length - 1; i > 0; i--) {
            if (shuffleIdx >= shuffleBytes.length) {
                shuffleBytes = sha256Bytes(shuffleBytes);
                shuffleIdx = 0;
            }
            int j = (shuffleBytes[shuffleIdx] & 0xFF) % (i + 1);
            shuffleIdx++;
            // swap
            char tmp = chars.get(i);
            chars.set(i, chars.get(j));
            chars.set(j, tmp);
        }

        StringBuilder result = new StringBuilder();
        for (char c : chars) result.append(c);
        return result.toString();
    }

    private static byte[] expandBytes(String input, int needed) {
        byte[] result = new byte[0];
        int counter = 0;
        while (result.length < needed) {
            byte[] hash = sha256Bytes((input + "|" + counter).getBytes(StandardCharsets.UTF_8));
            byte[] tmp = new byte[result.length + hash.length];
            System.arraycopy(result, 0, tmp, 0, result.length);
            System.arraycopy(hash, 0, tmp, result.length, hash.length);
            result = tmp;
            counter++;
        }
        return result;
    }

    private static byte[] sha256Bytes(byte[] input) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            return md.digest(input);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}
