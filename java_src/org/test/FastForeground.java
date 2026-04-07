package org.test;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class FastForeground {
    public static void start(Service context) {
        String channelId = "jenny_java_sync";
        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        // 1. Мгновенно создаем канал
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId,
                    "JennyMonitor Tracker",
                    NotificationManager.IMPORTANCE_HIGH
            );
            if (nm != null) {
                nm.createNotificationChannel(channel);
            }
        }

        // 2. Настраиваем клик по шторке
        Intent intent = new Intent(context, org.kivy.android.PythonActivity.class);
        // FLAG_IMMUTABLE (67108864) обязателен для новых Android
        PendingIntent pendingIntent = PendingIntent.getActivity(
                context, 0, intent, 67108864 
        );

        // 3. Собираем уведомление нативными средствами
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(context, channelId);
        } else {
            builder = new Notification.Builder(context);
        }

        builder.setContentTitle("JennyMonitor")
               .setContentText("Мониторинг активен (Java Core)")
               .setSmallIcon(android.R.drawable.ic_menu_info_details)
               .setContentIntent(pendingIntent)
               .setOngoing(true);

        // 4. Мгновенный запуск. Тип 1 = dataSync
        try {
            if (Build.VERSION.SDK_INT >= 29) {
                context.startForeground(1, builder.build(), 1);
            } else {
                context.startForeground(1, builder.build());
            }
        } catch (Exception e) {
            context.startForeground(1, builder.build());
        }
    }
}
