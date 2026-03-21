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
import com.rehab.robotarm.data.database.entity.Exercise;
import com.rehab.robotarm.data.database.entity.TrainingPlan;
import com.rehab.robotarm.data.database.entity.WeekPlan;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class TrainingPlanDao_Impl implements TrainingPlanDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<TrainingPlan> __insertionAdapterOfTrainingPlan;

  private final EntityInsertionAdapter<WeekPlan> __insertionAdapterOfWeekPlan;

  private final EntityInsertionAdapter<Exercise> __insertionAdapterOfExercise;

  private final EntityDeletionOrUpdateAdapter<TrainingPlan> __updateAdapterOfTrainingPlan;

  private final SharedSQLiteStatement __preparedStmtOfDeactivateAllPlans;

  public TrainingPlanDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfTrainingPlan = new EntityInsertionAdapter<TrainingPlan>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `training_plans` (`id`,`patientId`,`name`,`description`,`totalWeeks`,`goals`,`createdAt`,`isActive`) VALUES (?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingPlan entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getPatientId());
        statement.bindString(3, entity.getName());
        statement.bindString(4, entity.getDescription());
        statement.bindLong(5, entity.getTotalWeeks());
        statement.bindString(6, entity.getGoals());
        statement.bindLong(7, entity.getCreatedAt());
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(8, _tmp);
      }
    };
    this.__insertionAdapterOfWeekPlan = new EntityInsertionAdapter<WeekPlan>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `week_plans` (`id`,`planId`,`weekNumber`,`frequency`,`duration`,`exercises`) VALUES (?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final WeekPlan entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getPlanId());
        statement.bindLong(3, entity.getWeekNumber());
        statement.bindLong(4, entity.getFrequency());
        statement.bindLong(5, entity.getDuration());
        statement.bindString(6, entity.getExercises());
      }
    };
    this.__insertionAdapterOfExercise = new EntityInsertionAdapter<Exercise>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `exercises` (`id`,`weekPlanId`,`name`,`targetAngle`,`repetitions`,`restTime`,`difficulty`,`instructions`) VALUES (?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final Exercise entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getWeekPlanId());
        statement.bindString(3, entity.getName());
        statement.bindDouble(4, entity.getTargetAngle());
        statement.bindLong(5, entity.getRepetitions());
        statement.bindLong(6, entity.getRestTime());
        statement.bindString(7, entity.getDifficulty());
        statement.bindString(8, entity.getInstructions());
      }
    };
    this.__updateAdapterOfTrainingPlan = new EntityDeletionOrUpdateAdapter<TrainingPlan>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `training_plans` SET `id` = ?,`patientId` = ?,`name` = ?,`description` = ?,`totalWeeks` = ?,`goals` = ?,`createdAt` = ?,`isActive` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final TrainingPlan entity) {
        statement.bindString(1, entity.getId());
        statement.bindString(2, entity.getPatientId());
        statement.bindString(3, entity.getName());
        statement.bindString(4, entity.getDescription());
        statement.bindLong(5, entity.getTotalWeeks());
        statement.bindString(6, entity.getGoals());
        statement.bindLong(7, entity.getCreatedAt());
        final int _tmp = entity.isActive() ? 1 : 0;
        statement.bindLong(8, _tmp);
        statement.bindString(9, entity.getId());
      }
    };
    this.__preparedStmtOfDeactivateAllPlans = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "UPDATE training_plans SET isActive = 0 WHERE patientId = ?";
        return _query;
      }
    };
  }

  @Override
  public Object insertPlan(final TrainingPlan plan, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfTrainingPlan.insert(plan);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertWeekPlan(final WeekPlan weekPlan,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfWeekPlan.insert(weekPlan);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertExercise(final Exercise exercise,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfExercise.insert(exercise);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertExercises(final List<Exercise> exercises,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfExercise.insert(exercises);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updatePlan(final TrainingPlan plan, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfTrainingPlan.handle(plan);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deactivateAllPlans(final String patientId,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeactivateAllPlans.acquire();
        int _argIndex = 1;
        _stmt.bindString(_argIndex, patientId);
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
          __preparedStmtOfDeactivateAllPlans.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<TrainingPlan> getActivePlan(final String patientId) {
    final String _sql = "SELECT * FROM training_plans WHERE patientId = ? AND isActive = 1";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, patientId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"training_plans"}, new Callable<TrainingPlan>() {
      @Override
      @Nullable
      public TrainingPlan call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfTotalWeeks = CursorUtil.getColumnIndexOrThrow(_cursor, "totalWeeks");
          final int _cursorIndexOfGoals = CursorUtil.getColumnIndexOrThrow(_cursor, "goals");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final TrainingPlan _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpDescription;
            _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            final int _tmpTotalWeeks;
            _tmpTotalWeeks = _cursor.getInt(_cursorIndexOfTotalWeeks);
            final String _tmpGoals;
            _tmpGoals = _cursor.getString(_cursorIndexOfGoals);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            _result = new TrainingPlan(_tmpId,_tmpPatientId,_tmpName,_tmpDescription,_tmpTotalWeeks,_tmpGoals,_tmpCreatedAt,_tmpIsActive);
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

  @Override
  public Object getPlanById(final String planId,
      final Continuation<? super TrainingPlan> $completion) {
    final String _sql = "SELECT * FROM training_plans WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, planId);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<TrainingPlan>() {
      @Override
      @Nullable
      public TrainingPlan call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPatientId = CursorUtil.getColumnIndexOrThrow(_cursor, "patientId");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfTotalWeeks = CursorUtil.getColumnIndexOrThrow(_cursor, "totalWeeks");
          final int _cursorIndexOfGoals = CursorUtil.getColumnIndexOrThrow(_cursor, "goals");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfIsActive = CursorUtil.getColumnIndexOrThrow(_cursor, "isActive");
          final TrainingPlan _result;
          if (_cursor.moveToFirst()) {
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPatientId;
            _tmpPatientId = _cursor.getString(_cursorIndexOfPatientId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpDescription;
            _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            final int _tmpTotalWeeks;
            _tmpTotalWeeks = _cursor.getInt(_cursorIndexOfTotalWeeks);
            final String _tmpGoals;
            _tmpGoals = _cursor.getString(_cursorIndexOfGoals);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final boolean _tmpIsActive;
            final int _tmp;
            _tmp = _cursor.getInt(_cursorIndexOfIsActive);
            _tmpIsActive = _tmp != 0;
            _result = new TrainingPlan(_tmpId,_tmpPatientId,_tmpName,_tmpDescription,_tmpTotalWeeks,_tmpGoals,_tmpCreatedAt,_tmpIsActive);
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
  public Flow<List<WeekPlan>> getWeekPlans(final String planId) {
    final String _sql = "SELECT * FROM week_plans WHERE planId = ? ORDER BY weekNumber ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, planId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"week_plans"}, new Callable<List<WeekPlan>>() {
      @Override
      @NonNull
      public List<WeekPlan> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPlanId = CursorUtil.getColumnIndexOrThrow(_cursor, "planId");
          final int _cursorIndexOfWeekNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "weekNumber");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "duration");
          final int _cursorIndexOfExercises = CursorUtil.getColumnIndexOrThrow(_cursor, "exercises");
          final List<WeekPlan> _result = new ArrayList<WeekPlan>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final WeekPlan _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpPlanId;
            _tmpPlanId = _cursor.getString(_cursorIndexOfPlanId);
            final int _tmpWeekNumber;
            _tmpWeekNumber = _cursor.getInt(_cursorIndexOfWeekNumber);
            final int _tmpFrequency;
            _tmpFrequency = _cursor.getInt(_cursorIndexOfFrequency);
            final int _tmpDuration;
            _tmpDuration = _cursor.getInt(_cursorIndexOfDuration);
            final String _tmpExercises;
            _tmpExercises = _cursor.getString(_cursorIndexOfExercises);
            _item = new WeekPlan(_tmpId,_tmpPlanId,_tmpWeekNumber,_tmpFrequency,_tmpDuration,_tmpExercises);
            _result.add(_item);
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

  @Override
  public Flow<List<Exercise>> getExercises(final String weekPlanId) {
    final String _sql = "SELECT * FROM exercises WHERE weekPlanId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, weekPlanId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"exercises"}, new Callable<List<Exercise>>() {
      @Override
      @NonNull
      public List<Exercise> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfWeekPlanId = CursorUtil.getColumnIndexOrThrow(_cursor, "weekPlanId");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfTargetAngle = CursorUtil.getColumnIndexOrThrow(_cursor, "targetAngle");
          final int _cursorIndexOfRepetitions = CursorUtil.getColumnIndexOrThrow(_cursor, "repetitions");
          final int _cursorIndexOfRestTime = CursorUtil.getColumnIndexOrThrow(_cursor, "restTime");
          final int _cursorIndexOfDifficulty = CursorUtil.getColumnIndexOrThrow(_cursor, "difficulty");
          final int _cursorIndexOfInstructions = CursorUtil.getColumnIndexOrThrow(_cursor, "instructions");
          final List<Exercise> _result = new ArrayList<Exercise>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final Exercise _item;
            final String _tmpId;
            _tmpId = _cursor.getString(_cursorIndexOfId);
            final String _tmpWeekPlanId;
            _tmpWeekPlanId = _cursor.getString(_cursorIndexOfWeekPlanId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final float _tmpTargetAngle;
            _tmpTargetAngle = _cursor.getFloat(_cursorIndexOfTargetAngle);
            final int _tmpRepetitions;
            _tmpRepetitions = _cursor.getInt(_cursorIndexOfRepetitions);
            final int _tmpRestTime;
            _tmpRestTime = _cursor.getInt(_cursorIndexOfRestTime);
            final String _tmpDifficulty;
            _tmpDifficulty = _cursor.getString(_cursorIndexOfDifficulty);
            final String _tmpInstructions;
            _tmpInstructions = _cursor.getString(_cursorIndexOfInstructions);
            _item = new Exercise(_tmpId,_tmpWeekPlanId,_tmpName,_tmpTargetAngle,_tmpRepetitions,_tmpRestTime,_tmpDifficulty,_tmpInstructions);
            _result.add(_item);
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
