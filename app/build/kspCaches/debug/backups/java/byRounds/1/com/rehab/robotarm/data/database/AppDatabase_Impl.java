package com.rehab.robotarm.data.database;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import com.rehab.robotarm.data.database.dao.AchievementDao;
import com.rehab.robotarm.data.database.dao.AchievementDao_Impl;
import com.rehab.robotarm.data.database.dao.LeaderboardDao;
import com.rehab.robotarm.data.database.dao.LeaderboardDao_Impl;
import com.rehab.robotarm.data.database.dao.PatientDao;
import com.rehab.robotarm.data.database.dao.PatientDao_Impl;
import com.rehab.robotarm.data.database.dao.RehabAssessmentDao;
import com.rehab.robotarm.data.database.dao.RehabAssessmentDao_Impl;
import com.rehab.robotarm.data.database.dao.SensorRecordDao;
import com.rehab.robotarm.data.database.dao.SensorRecordDao_Impl;
import com.rehab.robotarm.data.database.dao.TrainingPlanDao;
import com.rehab.robotarm.data.database.dao.TrainingPlanDao_Impl;
import com.rehab.robotarm.data.database.dao.TrainingRecordDao;
import com.rehab.robotarm.data.database.dao.TrainingRecordDao_Impl;
import com.rehab.robotarm.data.database.dao.TrainingSessionDao;
import com.rehab.robotarm.data.database.dao.TrainingSessionDao_Impl;
import com.rehab.robotarm.data.database.dao.UserDao;
import com.rehab.robotarm.data.database.dao.UserDao_Impl;
import com.rehab.robotarm.data.database.dao.UserProfileDao;
import com.rehab.robotarm.data.database.dao.UserProfileDao_Impl;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class AppDatabase_Impl extends AppDatabase {
  private volatile UserDao _userDao;

  private volatile UserProfileDao _userProfileDao;

  private volatile PatientDao _patientDao;

  private volatile TrainingSessionDao _trainingSessionDao;

  private volatile TrainingRecordDao _trainingRecordDao;

  private volatile LeaderboardDao _leaderboardDao;

  private volatile AchievementDao _achievementDao;

  private volatile TrainingPlanDao _trainingPlanDao;

  private volatile SensorRecordDao _sensorRecordDao;

  private volatile RehabAssessmentDao _rehabAssessmentDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(2) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `users` (`id` TEXT NOT NULL, `username` TEXT NOT NULL, `password` TEXT NOT NULL, `email` TEXT NOT NULL, `phoneNumber` TEXT, `role` TEXT NOT NULL, `avatarUrl` TEXT, `createdAt` INTEGER NOT NULL, `lastLoginAt` INTEGER NOT NULL, `isActive` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `user_profiles` (`userId` TEXT NOT NULL, `displayName` TEXT NOT NULL, `age` INTEGER NOT NULL, `gender` TEXT NOT NULL, `diagnosis` TEXT, `hospitalId` TEXT, `doctorId` TEXT, `level` INTEGER NOT NULL, `experience` INTEGER NOT NULL, `totalTrainingSessions` INTEGER NOT NULL, `totalTrainingTime` INTEGER NOT NULL, `achievements` TEXT NOT NULL, PRIMARY KEY(`userId`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `patients` (`id` TEXT NOT NULL, `name` TEXT NOT NULL, `age` INTEGER NOT NULL, `gender` TEXT NOT NULL, `diagnosis` TEXT NOT NULL, `affectedSide` TEXT NOT NULL, `admissionDate` INTEGER NOT NULL, `doctorId` TEXT NOT NULL, `phoneNumber` TEXT NOT NULL, `notes` TEXT NOT NULL, `currentROM` REAL NOT NULL, `strengthLevel` INTEGER NOT NULL, `latestScore` REAL NOT NULL, `isActive` INTEGER NOT NULL, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `training_sessions` (`id` TEXT NOT NULL, `patientId` TEXT NOT NULL, `startTime` INTEGER NOT NULL, `endTime` INTEGER NOT NULL, `duration` INTEGER NOT NULL, `mode` TEXT NOT NULL, `maxShoulderAngle` REAL NOT NULL, `maxElbowAngle` REAL NOT NULL, `maxAngle` REAL NOT NULL, `minAngle` REAL NOT NULL, `targetAngle` REAL NOT NULL, `avgHeartRate` INTEGER, `maxHeartRate` INTEGER NOT NULL, `avgEmg` REAL NOT NULL, `avgEmgCh1` REAL NOT NULL, `avgEmgCh2` REAL NOT NULL, `repetitions` INTEGER NOT NULL, `overallScore` REAL NOT NULL, `painLevel` INTEGER NOT NULL, `fatigueLevel` INTEGER NOT NULL, `notes` TEXT NOT NULL, `isSynced` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `training_records` (`id` TEXT NOT NULL, `sessionId` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `shoulderAngle` REAL NOT NULL, `elbowAngle` REAL NOT NULL, `wristAngle` REAL NOT NULL, `emgCh1` REAL NOT NULL, `emgCh2` REAL NOT NULL, `heartRate` INTEGER NOT NULL, `spo2` INTEGER NOT NULL, `torqueX` REAL NOT NULL, `torqueY` REAL NOT NULL, `torqueZ` REAL NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `leaderboard_entries` (`id` TEXT NOT NULL, `userId` TEXT NOT NULL, `username` TEXT NOT NULL, `avatarUrl` TEXT, `score` INTEGER NOT NULL, `level` INTEGER NOT NULL, `totalSessions` INTEGER NOT NULL, `totalDuration` INTEGER NOT NULL, `maxAngle` REAL NOT NULL, `bestGameScore` INTEGER NOT NULL, `achievements` INTEGER NOT NULL, `rank` INTEGER NOT NULL, `category` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `achievements` (`id` TEXT NOT NULL, `userId` TEXT NOT NULL, `name` TEXT NOT NULL, `description` TEXT NOT NULL, `iconUrl` TEXT, `unlockedAt` INTEGER NOT NULL, `category` TEXT NOT NULL, `points` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `training_plans` (`id` TEXT NOT NULL, `patientId` TEXT NOT NULL, `name` TEXT NOT NULL, `description` TEXT NOT NULL, `totalWeeks` INTEGER NOT NULL, `goals` TEXT NOT NULL, `createdAt` INTEGER NOT NULL, `isActive` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `week_plans` (`id` TEXT NOT NULL, `planId` TEXT NOT NULL, `weekNumber` INTEGER NOT NULL, `frequency` INTEGER NOT NULL, `duration` INTEGER NOT NULL, `exercises` TEXT NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `exercises` (`id` TEXT NOT NULL, `weekPlanId` TEXT NOT NULL, `name` TEXT NOT NULL, `targetAngle` REAL NOT NULL, `repetitions` INTEGER NOT NULL, `restTime` INTEGER NOT NULL, `difficulty` TEXT NOT NULL, `instructions` TEXT NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `sensor_records` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `sessionId` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `shoulderAngle` REAL NOT NULL, `elbowAngle` REAL NOT NULL, `wristAngle` REAL NOT NULL, `lateralPosition` REAL NOT NULL, `shoulderTorque` REAL NOT NULL, `elbowTorque` REAL NOT NULL, `wristTorque` REAL NOT NULL, `shoulderForce` REAL NOT NULL, `elbowForce` REAL NOT NULL, `emgCh1` REAL NOT NULL, `emgCh2` REAL NOT NULL, `imuAccelX` REAL NOT NULL, `imuAccelY` REAL NOT NULL, `imuAccelZ` REAL NOT NULL, `imuGyroX` REAL NOT NULL, `imuGyroY` REAL NOT NULL, `imuGyroZ` REAL NOT NULL, `heartRate` INTEGER NOT NULL, `spo2` INTEGER NOT NULL, `shoulderTemp` REAL NOT NULL, `elbowTemp` REAL NOT NULL, `lateralTemp` REAL NOT NULL, FOREIGN KEY(`sessionId`) REFERENCES `training_sessions`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_sensor_records_sessionId` ON `sensor_records` (`sessionId`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_sensor_records_timestamp` ON `sensor_records` (`timestamp`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `rehab_assessments` (`id` TEXT NOT NULL, `sessionId` TEXT NOT NULL, `smoothness` REAL NOT NULL, `rangeOfMotion` REAL NOT NULL, `strength` REAL NOT NULL, `overallScore` REAL NOT NULL, `recommendation` TEXT NOT NULL, `cloudRecommendation` TEXT, `timestamp` INTEGER NOT NULL, PRIMARY KEY(`id`), FOREIGN KEY(`sessionId`) REFERENCES `training_sessions`(`id`) ON UPDATE NO ACTION ON DELETE CASCADE )");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_rehab_assessments_sessionId` ON `rehab_assessments` (`sessionId`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, '9b30f3a683d34417baafa173c1b3e25f')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `users`");
        db.execSQL("DROP TABLE IF EXISTS `user_profiles`");
        db.execSQL("DROP TABLE IF EXISTS `patients`");
        db.execSQL("DROP TABLE IF EXISTS `training_sessions`");
        db.execSQL("DROP TABLE IF EXISTS `training_records`");
        db.execSQL("DROP TABLE IF EXISTS `leaderboard_entries`");
        db.execSQL("DROP TABLE IF EXISTS `achievements`");
        db.execSQL("DROP TABLE IF EXISTS `training_plans`");
        db.execSQL("DROP TABLE IF EXISTS `week_plans`");
        db.execSQL("DROP TABLE IF EXISTS `exercises`");
        db.execSQL("DROP TABLE IF EXISTS `sensor_records`");
        db.execSQL("DROP TABLE IF EXISTS `rehab_assessments`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        db.execSQL("PRAGMA foreign_keys = ON");
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsUsers = new HashMap<String, TableInfo.Column>(10);
        _columnsUsers.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("username", new TableInfo.Column("username", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("password", new TableInfo.Column("password", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("email", new TableInfo.Column("email", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("phoneNumber", new TableInfo.Column("phoneNumber", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("role", new TableInfo.Column("role", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("avatarUrl", new TableInfo.Column("avatarUrl", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("lastLoginAt", new TableInfo.Column("lastLoginAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("isActive", new TableInfo.Column("isActive", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysUsers = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesUsers = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoUsers = new TableInfo("users", _columnsUsers, _foreignKeysUsers, _indicesUsers);
        final TableInfo _existingUsers = TableInfo.read(db, "users");
        if (!_infoUsers.equals(_existingUsers)) {
          return new RoomOpenHelper.ValidationResult(false, "users(com.rehab.robotarm.data.database.entity.User).\n"
                  + " Expected:\n" + _infoUsers + "\n"
                  + " Found:\n" + _existingUsers);
        }
        final HashMap<String, TableInfo.Column> _columnsUserProfiles = new HashMap<String, TableInfo.Column>(12);
        _columnsUserProfiles.put("userId", new TableInfo.Column("userId", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("displayName", new TableInfo.Column("displayName", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("age", new TableInfo.Column("age", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("gender", new TableInfo.Column("gender", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("diagnosis", new TableInfo.Column("diagnosis", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("hospitalId", new TableInfo.Column("hospitalId", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("doctorId", new TableInfo.Column("doctorId", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("level", new TableInfo.Column("level", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("experience", new TableInfo.Column("experience", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("totalTrainingSessions", new TableInfo.Column("totalTrainingSessions", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("totalTrainingTime", new TableInfo.Column("totalTrainingTime", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUserProfiles.put("achievements", new TableInfo.Column("achievements", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysUserProfiles = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesUserProfiles = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoUserProfiles = new TableInfo("user_profiles", _columnsUserProfiles, _foreignKeysUserProfiles, _indicesUserProfiles);
        final TableInfo _existingUserProfiles = TableInfo.read(db, "user_profiles");
        if (!_infoUserProfiles.equals(_existingUserProfiles)) {
          return new RoomOpenHelper.ValidationResult(false, "user_profiles(com.rehab.robotarm.data.database.entity.UserProfile).\n"
                  + " Expected:\n" + _infoUserProfiles + "\n"
                  + " Found:\n" + _existingUserProfiles);
        }
        final HashMap<String, TableInfo.Column> _columnsPatients = new HashMap<String, TableInfo.Column>(16);
        _columnsPatients.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("age", new TableInfo.Column("age", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("gender", new TableInfo.Column("gender", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("diagnosis", new TableInfo.Column("diagnosis", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("affectedSide", new TableInfo.Column("affectedSide", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("admissionDate", new TableInfo.Column("admissionDate", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("doctorId", new TableInfo.Column("doctorId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("phoneNumber", new TableInfo.Column("phoneNumber", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("notes", new TableInfo.Column("notes", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("currentROM", new TableInfo.Column("currentROM", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("strengthLevel", new TableInfo.Column("strengthLevel", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("latestScore", new TableInfo.Column("latestScore", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("isActive", new TableInfo.Column("isActive", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPatients.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysPatients = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesPatients = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoPatients = new TableInfo("patients", _columnsPatients, _foreignKeysPatients, _indicesPatients);
        final TableInfo _existingPatients = TableInfo.read(db, "patients");
        if (!_infoPatients.equals(_existingPatients)) {
          return new RoomOpenHelper.ValidationResult(false, "patients(com.rehab.robotarm.data.database.entity.Patient).\n"
                  + " Expected:\n" + _infoPatients + "\n"
                  + " Found:\n" + _existingPatients);
        }
        final HashMap<String, TableInfo.Column> _columnsTrainingSessions = new HashMap<String, TableInfo.Column>(22);
        _columnsTrainingSessions.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("patientId", new TableInfo.Column("patientId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("startTime", new TableInfo.Column("startTime", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("endTime", new TableInfo.Column("endTime", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("duration", new TableInfo.Column("duration", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("mode", new TableInfo.Column("mode", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("maxShoulderAngle", new TableInfo.Column("maxShoulderAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("maxElbowAngle", new TableInfo.Column("maxElbowAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("maxAngle", new TableInfo.Column("maxAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("minAngle", new TableInfo.Column("minAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("targetAngle", new TableInfo.Column("targetAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("avgHeartRate", new TableInfo.Column("avgHeartRate", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("maxHeartRate", new TableInfo.Column("maxHeartRate", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("avgEmg", new TableInfo.Column("avgEmg", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("avgEmgCh1", new TableInfo.Column("avgEmgCh1", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("avgEmgCh2", new TableInfo.Column("avgEmgCh2", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("repetitions", new TableInfo.Column("repetitions", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("overallScore", new TableInfo.Column("overallScore", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("painLevel", new TableInfo.Column("painLevel", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("fatigueLevel", new TableInfo.Column("fatigueLevel", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("notes", new TableInfo.Column("notes", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingSessions.put("isSynced", new TableInfo.Column("isSynced", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysTrainingSessions = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesTrainingSessions = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoTrainingSessions = new TableInfo("training_sessions", _columnsTrainingSessions, _foreignKeysTrainingSessions, _indicesTrainingSessions);
        final TableInfo _existingTrainingSessions = TableInfo.read(db, "training_sessions");
        if (!_infoTrainingSessions.equals(_existingTrainingSessions)) {
          return new RoomOpenHelper.ValidationResult(false, "training_sessions(com.rehab.robotarm.data.database.entity.TrainingSession).\n"
                  + " Expected:\n" + _infoTrainingSessions + "\n"
                  + " Found:\n" + _existingTrainingSessions);
        }
        final HashMap<String, TableInfo.Column> _columnsTrainingRecords = new HashMap<String, TableInfo.Column>(13);
        _columnsTrainingRecords.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("sessionId", new TableInfo.Column("sessionId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("shoulderAngle", new TableInfo.Column("shoulderAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("elbowAngle", new TableInfo.Column("elbowAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("wristAngle", new TableInfo.Column("wristAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("emgCh1", new TableInfo.Column("emgCh1", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("emgCh2", new TableInfo.Column("emgCh2", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("heartRate", new TableInfo.Column("heartRate", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("spo2", new TableInfo.Column("spo2", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("torqueX", new TableInfo.Column("torqueX", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("torqueY", new TableInfo.Column("torqueY", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingRecords.put("torqueZ", new TableInfo.Column("torqueZ", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysTrainingRecords = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesTrainingRecords = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoTrainingRecords = new TableInfo("training_records", _columnsTrainingRecords, _foreignKeysTrainingRecords, _indicesTrainingRecords);
        final TableInfo _existingTrainingRecords = TableInfo.read(db, "training_records");
        if (!_infoTrainingRecords.equals(_existingTrainingRecords)) {
          return new RoomOpenHelper.ValidationResult(false, "training_records(com.rehab.robotarm.data.database.entity.TrainingRecord).\n"
                  + " Expected:\n" + _infoTrainingRecords + "\n"
                  + " Found:\n" + _existingTrainingRecords);
        }
        final HashMap<String, TableInfo.Column> _columnsLeaderboardEntries = new HashMap<String, TableInfo.Column>(14);
        _columnsLeaderboardEntries.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("userId", new TableInfo.Column("userId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("username", new TableInfo.Column("username", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("avatarUrl", new TableInfo.Column("avatarUrl", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("score", new TableInfo.Column("score", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("level", new TableInfo.Column("level", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("totalSessions", new TableInfo.Column("totalSessions", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("totalDuration", new TableInfo.Column("totalDuration", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("maxAngle", new TableInfo.Column("maxAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("bestGameScore", new TableInfo.Column("bestGameScore", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("achievements", new TableInfo.Column("achievements", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("rank", new TableInfo.Column("rank", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("category", new TableInfo.Column("category", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsLeaderboardEntries.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysLeaderboardEntries = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesLeaderboardEntries = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoLeaderboardEntries = new TableInfo("leaderboard_entries", _columnsLeaderboardEntries, _foreignKeysLeaderboardEntries, _indicesLeaderboardEntries);
        final TableInfo _existingLeaderboardEntries = TableInfo.read(db, "leaderboard_entries");
        if (!_infoLeaderboardEntries.equals(_existingLeaderboardEntries)) {
          return new RoomOpenHelper.ValidationResult(false, "leaderboard_entries(com.rehab.robotarm.data.database.entity.LeaderboardEntry).\n"
                  + " Expected:\n" + _infoLeaderboardEntries + "\n"
                  + " Found:\n" + _existingLeaderboardEntries);
        }
        final HashMap<String, TableInfo.Column> _columnsAchievements = new HashMap<String, TableInfo.Column>(8);
        _columnsAchievements.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("userId", new TableInfo.Column("userId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("description", new TableInfo.Column("description", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("iconUrl", new TableInfo.Column("iconUrl", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("unlockedAt", new TableInfo.Column("unlockedAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("category", new TableInfo.Column("category", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAchievements.put("points", new TableInfo.Column("points", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysAchievements = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesAchievements = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoAchievements = new TableInfo("achievements", _columnsAchievements, _foreignKeysAchievements, _indicesAchievements);
        final TableInfo _existingAchievements = TableInfo.read(db, "achievements");
        if (!_infoAchievements.equals(_existingAchievements)) {
          return new RoomOpenHelper.ValidationResult(false, "achievements(com.rehab.robotarm.data.database.entity.Achievement).\n"
                  + " Expected:\n" + _infoAchievements + "\n"
                  + " Found:\n" + _existingAchievements);
        }
        final HashMap<String, TableInfo.Column> _columnsTrainingPlans = new HashMap<String, TableInfo.Column>(8);
        _columnsTrainingPlans.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("patientId", new TableInfo.Column("patientId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("description", new TableInfo.Column("description", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("totalWeeks", new TableInfo.Column("totalWeeks", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("goals", new TableInfo.Column("goals", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsTrainingPlans.put("isActive", new TableInfo.Column("isActive", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysTrainingPlans = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesTrainingPlans = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoTrainingPlans = new TableInfo("training_plans", _columnsTrainingPlans, _foreignKeysTrainingPlans, _indicesTrainingPlans);
        final TableInfo _existingTrainingPlans = TableInfo.read(db, "training_plans");
        if (!_infoTrainingPlans.equals(_existingTrainingPlans)) {
          return new RoomOpenHelper.ValidationResult(false, "training_plans(com.rehab.robotarm.data.database.entity.TrainingPlan).\n"
                  + " Expected:\n" + _infoTrainingPlans + "\n"
                  + " Found:\n" + _existingTrainingPlans);
        }
        final HashMap<String, TableInfo.Column> _columnsWeekPlans = new HashMap<String, TableInfo.Column>(6);
        _columnsWeekPlans.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWeekPlans.put("planId", new TableInfo.Column("planId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWeekPlans.put("weekNumber", new TableInfo.Column("weekNumber", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWeekPlans.put("frequency", new TableInfo.Column("frequency", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWeekPlans.put("duration", new TableInfo.Column("duration", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWeekPlans.put("exercises", new TableInfo.Column("exercises", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysWeekPlans = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesWeekPlans = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoWeekPlans = new TableInfo("week_plans", _columnsWeekPlans, _foreignKeysWeekPlans, _indicesWeekPlans);
        final TableInfo _existingWeekPlans = TableInfo.read(db, "week_plans");
        if (!_infoWeekPlans.equals(_existingWeekPlans)) {
          return new RoomOpenHelper.ValidationResult(false, "week_plans(com.rehab.robotarm.data.database.entity.WeekPlan).\n"
                  + " Expected:\n" + _infoWeekPlans + "\n"
                  + " Found:\n" + _existingWeekPlans);
        }
        final HashMap<String, TableInfo.Column> _columnsExercises = new HashMap<String, TableInfo.Column>(8);
        _columnsExercises.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("weekPlanId", new TableInfo.Column("weekPlanId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("targetAngle", new TableInfo.Column("targetAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("repetitions", new TableInfo.Column("repetitions", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("restTime", new TableInfo.Column("restTime", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("difficulty", new TableInfo.Column("difficulty", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsExercises.put("instructions", new TableInfo.Column("instructions", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysExercises = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesExercises = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoExercises = new TableInfo("exercises", _columnsExercises, _foreignKeysExercises, _indicesExercises);
        final TableInfo _existingExercises = TableInfo.read(db, "exercises");
        if (!_infoExercises.equals(_existingExercises)) {
          return new RoomOpenHelper.ValidationResult(false, "exercises(com.rehab.robotarm.data.database.entity.Exercise).\n"
                  + " Expected:\n" + _infoExercises + "\n"
                  + " Found:\n" + _existingExercises);
        }
        final HashMap<String, TableInfo.Column> _columnsSensorRecords = new HashMap<String, TableInfo.Column>(25);
        _columnsSensorRecords.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("sessionId", new TableInfo.Column("sessionId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("shoulderAngle", new TableInfo.Column("shoulderAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("elbowAngle", new TableInfo.Column("elbowAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("wristAngle", new TableInfo.Column("wristAngle", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("lateralPosition", new TableInfo.Column("lateralPosition", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("shoulderTorque", new TableInfo.Column("shoulderTorque", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("elbowTorque", new TableInfo.Column("elbowTorque", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("wristTorque", new TableInfo.Column("wristTorque", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("shoulderForce", new TableInfo.Column("shoulderForce", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("elbowForce", new TableInfo.Column("elbowForce", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("emgCh1", new TableInfo.Column("emgCh1", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("emgCh2", new TableInfo.Column("emgCh2", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuAccelX", new TableInfo.Column("imuAccelX", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuAccelY", new TableInfo.Column("imuAccelY", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuAccelZ", new TableInfo.Column("imuAccelZ", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuGyroX", new TableInfo.Column("imuGyroX", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuGyroY", new TableInfo.Column("imuGyroY", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("imuGyroZ", new TableInfo.Column("imuGyroZ", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("heartRate", new TableInfo.Column("heartRate", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("spo2", new TableInfo.Column("spo2", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("shoulderTemp", new TableInfo.Column("shoulderTemp", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("elbowTemp", new TableInfo.Column("elbowTemp", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsSensorRecords.put("lateralTemp", new TableInfo.Column("lateralTemp", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysSensorRecords = new HashSet<TableInfo.ForeignKey>(1);
        _foreignKeysSensorRecords.add(new TableInfo.ForeignKey("training_sessions", "CASCADE", "NO ACTION", Arrays.asList("sessionId"), Arrays.asList("id")));
        final HashSet<TableInfo.Index> _indicesSensorRecords = new HashSet<TableInfo.Index>(2);
        _indicesSensorRecords.add(new TableInfo.Index("index_sensor_records_sessionId", false, Arrays.asList("sessionId"), Arrays.asList("ASC")));
        _indicesSensorRecords.add(new TableInfo.Index("index_sensor_records_timestamp", false, Arrays.asList("timestamp"), Arrays.asList("ASC")));
        final TableInfo _infoSensorRecords = new TableInfo("sensor_records", _columnsSensorRecords, _foreignKeysSensorRecords, _indicesSensorRecords);
        final TableInfo _existingSensorRecords = TableInfo.read(db, "sensor_records");
        if (!_infoSensorRecords.equals(_existingSensorRecords)) {
          return new RoomOpenHelper.ValidationResult(false, "sensor_records(com.rehab.robotarm.data.database.entity.SensorRecord).\n"
                  + " Expected:\n" + _infoSensorRecords + "\n"
                  + " Found:\n" + _existingSensorRecords);
        }
        final HashMap<String, TableInfo.Column> _columnsRehabAssessments = new HashMap<String, TableInfo.Column>(9);
        _columnsRehabAssessments.put("id", new TableInfo.Column("id", "TEXT", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("sessionId", new TableInfo.Column("sessionId", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("smoothness", new TableInfo.Column("smoothness", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("rangeOfMotion", new TableInfo.Column("rangeOfMotion", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("strength", new TableInfo.Column("strength", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("overallScore", new TableInfo.Column("overallScore", "REAL", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("recommendation", new TableInfo.Column("recommendation", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("cloudRecommendation", new TableInfo.Column("cloudRecommendation", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsRehabAssessments.put("timestamp", new TableInfo.Column("timestamp", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysRehabAssessments = new HashSet<TableInfo.ForeignKey>(1);
        _foreignKeysRehabAssessments.add(new TableInfo.ForeignKey("training_sessions", "CASCADE", "NO ACTION", Arrays.asList("sessionId"), Arrays.asList("id")));
        final HashSet<TableInfo.Index> _indicesRehabAssessments = new HashSet<TableInfo.Index>(1);
        _indicesRehabAssessments.add(new TableInfo.Index("index_rehab_assessments_sessionId", false, Arrays.asList("sessionId"), Arrays.asList("ASC")));
        final TableInfo _infoRehabAssessments = new TableInfo("rehab_assessments", _columnsRehabAssessments, _foreignKeysRehabAssessments, _indicesRehabAssessments);
        final TableInfo _existingRehabAssessments = TableInfo.read(db, "rehab_assessments");
        if (!_infoRehabAssessments.equals(_existingRehabAssessments)) {
          return new RoomOpenHelper.ValidationResult(false, "rehab_assessments(com.rehab.robotarm.data.database.entity.RehabAssessment).\n"
                  + " Expected:\n" + _infoRehabAssessments + "\n"
                  + " Found:\n" + _existingRehabAssessments);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "9b30f3a683d34417baafa173c1b3e25f", "ad3958d631121336701c01d3e7b5d16e");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "users","user_profiles","patients","training_sessions","training_records","leaderboard_entries","achievements","training_plans","week_plans","exercises","sensor_records","rehab_assessments");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    final boolean _supportsDeferForeignKeys = android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP;
    try {
      if (!_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA foreign_keys = FALSE");
      }
      super.beginTransaction();
      if (_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA defer_foreign_keys = TRUE");
      }
      _db.execSQL("DELETE FROM `users`");
      _db.execSQL("DELETE FROM `user_profiles`");
      _db.execSQL("DELETE FROM `patients`");
      _db.execSQL("DELETE FROM `training_sessions`");
      _db.execSQL("DELETE FROM `training_records`");
      _db.execSQL("DELETE FROM `leaderboard_entries`");
      _db.execSQL("DELETE FROM `achievements`");
      _db.execSQL("DELETE FROM `training_plans`");
      _db.execSQL("DELETE FROM `week_plans`");
      _db.execSQL("DELETE FROM `exercises`");
      _db.execSQL("DELETE FROM `sensor_records`");
      _db.execSQL("DELETE FROM `rehab_assessments`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      if (!_supportsDeferForeignKeys) {
        _db.execSQL("PRAGMA foreign_keys = TRUE");
      }
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(UserDao.class, UserDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(UserProfileDao.class, UserProfileDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(PatientDao.class, PatientDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(TrainingSessionDao.class, TrainingSessionDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(TrainingRecordDao.class, TrainingRecordDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(LeaderboardDao.class, LeaderboardDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(AchievementDao.class, AchievementDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(TrainingPlanDao.class, TrainingPlanDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(SensorRecordDao.class, SensorRecordDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(RehabAssessmentDao.class, RehabAssessmentDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public UserDao userDao() {
    if (_userDao != null) {
      return _userDao;
    } else {
      synchronized(this) {
        if(_userDao == null) {
          _userDao = new UserDao_Impl(this);
        }
        return _userDao;
      }
    }
  }

  @Override
  public UserProfileDao userProfileDao() {
    if (_userProfileDao != null) {
      return _userProfileDao;
    } else {
      synchronized(this) {
        if(_userProfileDao == null) {
          _userProfileDao = new UserProfileDao_Impl(this);
        }
        return _userProfileDao;
      }
    }
  }

  @Override
  public PatientDao patientDao() {
    if (_patientDao != null) {
      return _patientDao;
    } else {
      synchronized(this) {
        if(_patientDao == null) {
          _patientDao = new PatientDao_Impl(this);
        }
        return _patientDao;
      }
    }
  }

  @Override
  public TrainingSessionDao trainingSessionDao() {
    if (_trainingSessionDao != null) {
      return _trainingSessionDao;
    } else {
      synchronized(this) {
        if(_trainingSessionDao == null) {
          _trainingSessionDao = new TrainingSessionDao_Impl(this);
        }
        return _trainingSessionDao;
      }
    }
  }

  @Override
  public TrainingRecordDao trainingRecordDao() {
    if (_trainingRecordDao != null) {
      return _trainingRecordDao;
    } else {
      synchronized(this) {
        if(_trainingRecordDao == null) {
          _trainingRecordDao = new TrainingRecordDao_Impl(this);
        }
        return _trainingRecordDao;
      }
    }
  }

  @Override
  public LeaderboardDao leaderboardDao() {
    if (_leaderboardDao != null) {
      return _leaderboardDao;
    } else {
      synchronized(this) {
        if(_leaderboardDao == null) {
          _leaderboardDao = new LeaderboardDao_Impl(this);
        }
        return _leaderboardDao;
      }
    }
  }

  @Override
  public AchievementDao achievementDao() {
    if (_achievementDao != null) {
      return _achievementDao;
    } else {
      synchronized(this) {
        if(_achievementDao == null) {
          _achievementDao = new AchievementDao_Impl(this);
        }
        return _achievementDao;
      }
    }
  }

  @Override
  public TrainingPlanDao trainingPlanDao() {
    if (_trainingPlanDao != null) {
      return _trainingPlanDao;
    } else {
      synchronized(this) {
        if(_trainingPlanDao == null) {
          _trainingPlanDao = new TrainingPlanDao_Impl(this);
        }
        return _trainingPlanDao;
      }
    }
  }

  @Override
  public SensorRecordDao sensorRecordDao() {
    if (_sensorRecordDao != null) {
      return _sensorRecordDao;
    } else {
      synchronized(this) {
        if(_sensorRecordDao == null) {
          _sensorRecordDao = new SensorRecordDao_Impl(this);
        }
        return _sensorRecordDao;
      }
    }
  }

  @Override
  public RehabAssessmentDao rehabAssessmentDao() {
    if (_rehabAssessmentDao != null) {
      return _rehabAssessmentDao;
    } else {
      synchronized(this) {
        if(_rehabAssessmentDao == null) {
          _rehabAssessmentDao = new RehabAssessmentDao_Impl(this);
        }
        return _rehabAssessmentDao;
      }
    }
  }
}
