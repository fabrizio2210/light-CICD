package main

import (
  "testing"
  "github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
  "github.com/go-redis/redismock/v8"
)

func TestWaitForJob(t *testing.T) {
  var redisMock redismock.ClientMock
  rediswrapper.RedisClient, redisMock = redismock.NewClientMock()
  redisMock.ExpectBLPop(0, "executions").SetVal([]string{"test_execution"})
  WaitForJob()
}
