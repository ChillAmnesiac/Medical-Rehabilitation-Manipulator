package com.rehab.robotarm.data.database.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.rehab.robotarm.data.database.entity.UserProfile;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class UserProfileDao_Impl implements UserProfileDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<UserProfile> __insertionAdapterOfUserProfile;

  private final EntityDeletionOrUpdateAdapter<UserProfile> __updateAdapterOfUserProfile;

  private final SharedSQLiteStatement __preparedStmtOfUpdateLevelAndExp;

  private final SharedSQLiteStatement __preparedStmtOfIncrementTrainingStats;

  public UserProfileDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfUserProfile = new EntityInsertionAdapter<UserProfile>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `user_profiles` (`userId`,`displayName`,`age`,`gender`,`diagnosis`,`hospitalId`,`doctorId`,`level`,`experience`,`totalTrainingSessions`,`totalTrainingTime`,`achievements`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final UserProfile entity) {
        statement.bindString(1, entity.getUserId());
        statement.bindString(2, entity.getDisplayName());
        statement.bindLong(3, entity.getAge());
        statement.bindString(4, entity.getGender());
        if (entity.getDiagnosis() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDiagnosis());
        }
        if (entity.getHospitalId() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getHospitalId());
        }
        if (entity.getDoctorId() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getDoctorId());
        }
        statement.bindLong(8, entity.getLevel());
        statement.bindLong(9, entity.getExperience());
        statement.bindLong(10, entity.getTotalTrainingSessions());
        statement.bindLong(11, entity.getTotalTrainingTime());
        statement.bindString(12, entity.getAchievements());
      }
    };
    this.__updateAdapterOfUserProfile = new EntityDeletionOrUpdateAdapter<UserProfile>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `user_profiles` SET `userId` = ?,`displayName` = ?,`age` = ?,`gender` = ?,`diagnosis` = ?,`hospitalId` = ?,`doctorId` = ?,`level` = ?,`experience` = ?,`totalTrainingSessions` = ?,`totalTrainingTime` = ?,`achievements` = ? WHERE `userId` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final UserProfile entity) {
        statement.bindString(1, entity.getUserId());
        statement.bindString(2, entity.getDisplayName());
        statement.bindLong(3, entity.getAge());
        statement.bindString(4, entity.getGender());
        if (entity.getDiagnosis() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDiagnosis());
        }
        if (entity.getHospitalId() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getHospitalId());
        }
        if (entity.getDoctorId() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getDoctorId());
        }
        statement.bindLong(8, entity.getLevel());
        statement.bindLong(9, entity.getExperience());
        statement.bindLong(10, entity.getTotalTrainingSessions());
        statement.bindLong(11, entity.getTotalTrainingTime());
        statement.bindString(12, entity.getAchievements());
        statement.bindString(13, entity.getUserId());
      }
    };
    this.__preparedStmtOfUpdateLevelAndExp = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE user_profiles SET level = ?, experience = ? WHERE userId = ?";
        return _query;
      }
    };
    this.__preparedStmtOfIncrementTrainingStats = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE user_profiles SET totalTrainingSessions = totalTrainingSessions + 1, totalTrainingTime = totalTrainingTime + ? WHERE userId = ?";
        return _query;
      }
    };
  }

  @Override
  public Object createProfile(final UserProfile profile,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfUserProfile.insert(profile);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateProfile(final UserProfile profile,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfUserProfile.handle(profile);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateLevelAndExp(final String userId, final int level, final int experience,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfUpdateLevelAndExp.acquire();
        int _argIndex = 1;
        _stmt.bindLong(_argIndex, level);
        _argIndex = 2;
        _stmt.bindLong(_argIndex, experience);
        _argIndex = 3;
        _stmt.bindString(_argIndex, userId);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfUpdateLevelAndExp.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object incrementTrainingStats(final String userId, final long duration,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfIncrementTrainingStats.acquire();
        int _argIndex = 1;
        _stmt.bindLong(_argIndex, duration);
        _argIndex = 2;
        _stmt.bindString(_argIndex, userId);
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfIncrementTrainingStats.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Object getProfile(final String userId,
      final Continuation<? super UserProfile> $completion) {
    final String _sql = "SELECT * FROM user_profiles WHERE userId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, userId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<UserProfile>() {
      @Override
      @Nullable
      public UserProfile call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "userId");
          final int _cursorIndexOfDisplayName = CursorUtil.getColumnIndexOrThrow(_cursor, "displayName");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfHospitalId = CursorUtil.getColumnIndexOrThrow(_cursor, "hospitalId");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "level");
          final int _cursorIndexOfExperience = CursorUtil.getColumnIndexOrThrow(_cursor, "experience");
          final int _cursorIndexOfTotalTrainingSessions = CursorUtil.getColumnIndexOrThrow(_cursor, "totalTrainingSessions");
          final int _cursorIndexOfTotalTrainingTime = CursorUtil.getColumnIndexOrThrow(_cursor, "totalTrainingTime");
          final int _cursorIndexOfAchievements = CursorUtil.getColumnIndexOrThrow(_cursor, "achievements");
          final UserProfile _result;
          if (_cursor.moveToFirst()) {
            final String _tmpUserId;
            _tmpUserId = _cursor.getString(_cursorIndexOfUserId);
            final String _tmpDisplayName;
            _tmpDisplayName = _cursor.getString(_cursorIndexOfDisplayName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            if (_cursor.isNull(_cursorIndexOfDiagnosis)) {
              _tmpDiagnosis = null;
            } else {
              _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            }
            final String _tmpHospitalId;
            if (_cursor.isNull(_cursorIndexOfHospitalId)) {
              _tmpHospitalId = null;
            } else {
              _tmpHospitalId = _cursor.getString(_cursorIndexOfHospitalId);
            }
            final String _tmpDoctorId;
            if (_cursor.isNull(_cursorIndexOfDoctorId)) {
              _tmpDoctorId = null;
            } else {
              _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            }
            final int _tmpLevel;
            _tmpLevel = _cursor.getInt(_cursorIndexOfLevel);
            final int _tmpExperience;
            _tmpExperience = _cursor.getInt(_cursorIndexOfExperience);
            final int _tmpTotalTrainingSessions;
            _tmpTotalTrainingSessions = _cursor.getInt(_cursorIndexOfTotalTrainingSessions);
            final long _tmpTotalTrainingTime;
            _tmpTotalTrainingTime = _cursor.getLong(_cursorIndexOfTotalTrainingTime);
            final String _tmpAchievements;
            _tmpAchievements = _cursor.getString(_cursorIndexOfAchievements);
            _result = new UserProfile(_tmpUserId,_tmpDisplayName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpHospitalId,_tmpDoctorId,_tmpLevel,_tmpExperience,_tmpTotalTrainingSessions,_tmpTotalTrainingTime,_tmpAchievements);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Flow<UserProfile> getProfileFlow(final String userId) {
    final String _sql = "SELECT * FROM user_profiles WHERE userId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, userId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"user_profiles"}, new Callable<UserProfile>() {
      @Override
      @Nullable
      public UserProfile call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "userId");
          final int _cursorIndexOfDisplayName = CursorUtil.getColumnIndexOrThrow(_cursor, "displayName");
          final int _cursorIndexOfAge = CursorUtil.getColumnIndexOrThrow(_cursor, "age");
          final int _cursorIndexOfGender = CursorUtil.getColumnIndexOrThrow(_cursor, "gender");
          final int _cursorIndexOfDiagnosis = CursorUtil.getColumnIndexOrThrow(_cursor, "diagnosis");
          final int _cursorIndexOfHospitalId = CursorUtil.getColumnIndexOrThrow(_cursor, "hospitalId");
          final int _cursorIndexOfDoctorId = CursorUtil.getColumnIndexOrThrow(_cursor, "doctorId");
          final int _cursorIndexOfLevel = CursorUtil.getColumnIndexOrThrow(_cursor, "level");
          final int _cursorIndexOfExperience = CursorUtil.getColumnIndexOrThrow(_cursor, "experience");
          final int _cursorIndexOfTotalTrainingSessions = CursorUtil.getColumnIndexOrThrow(_cursor, "totalTrainingSessions");
          final int _cursorIndexOfTotalTrainingTime = CursorUtil.getColumnIndexOrThrow(_cursor, "totalTrainingTime");
          final int _cursorIndexOfAchievements = CursorUtil.getColumnIndexOrThrow(_cursor, "achievements");
          final UserProfile _result;
          if (_cursor.moveToFirst()) {
            final String _tmpUserId;
            _tmpUserId = _cursor.getString(_cursorIndexOfUserId);
            final String _tmpDisplayName;
            _tmpDisplayName = _cursor.getString(_cursorIndexOfDisplayName);
            final int _tmpAge;
            _tmpAge = _cursor.getInt(_cursorIndexOfAge);
            final String _tmpGender;
            _tmpGender = _cursor.getString(_cursorIndexOfGender);
            final String _tmpDiagnosis;
            if (_cursor.isNull(_cursorIndexOfDiagnosis)) {
              _tmpDiagnosis = null;
            } else {
              _tmpDiagnosis = _cursor.getString(_cursorIndexOfDiagnosis);
            }
            final String _tmpHospitalId;
            if (_cursor.isNull(_cursorIndexOfHospitalId)) {
              _tmpHospitalId = null;
            } else {
              _tmpHospitalId = _cursor.getString(_cursorIndexOfHospitalId);
            }
            final String _tmpDoctorId;
            if (_cursor.isNull(_cursorIndexOfDoctorId)) {
              _tmpDoctorId = null;
            } else {
              _tmpDoctorId = _cursor.getString(_cursorIndexOfDoctorId);
            }
            final int _tmpLevel;
            _tmpLevel = _cursor.getInt(_cursorIndexOfLevel);
            final int _tmpExperience;
            _tmpExperience = _cursor.getInt(_cursorIndexOfExperience);
            final int _tmpTotalTrainingSessions;
            _tmpTotalTrainingSessions = _cursor.getInt(_cursorIndexOfTotalTrainingSessions);
            final long _tmpTotalTrainingTime;
            _tmpTotalTrainingTime = _cursor.getLong(_cursorIndexOfTotalTrainingTime);
            final String _tmpAchievements;
            _tmpAchievements = _cursor.getString(_cursorIndexOfAchievements);
            _result = new UserProfile(_tmpUserId,_tmpDisplayName,_tmpAge,_tmpGender,_tmpDiagnosis,_tmpHospitalId,_tmpDoctorId,_tmpLevel,_tmpExperience,_tmpTotalTrainingSessions,_tmpTotalTrainingTime,_tmpAchievements);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
