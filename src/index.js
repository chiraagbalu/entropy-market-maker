"use strict"
require("dotenv").config()
const Sequelize = require("sequelize")
const db = {}
var parse = require("pg-connection-string")
// var readDBConfig = parse(process.env.TIMESCALEDB_URL_READ)


// @ts-ignore
var readDBConfig = parse("jdbc:postgresql://perpmarkets.c3jgxn9bw7cv.us-east-1.rds.amazonaws.com/postgres")
// @ts-ignore
var writeDBConfig = parse("jdbc:postgresql://perpmarkets.c3jgxn9bw7cv.us-east-1.rds.amazonaws.com/postgres")

// SET USERNAME AS readDBConfig.user etc.
// @ts-ignore
const sequelize = new Sequelize({
  host: process.env.DB_HOST,
  username: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  port: process.env.DB_PORT,
  replication: {
    read: [{ host: 'perpmarkets.c3jgxn9bw7cv.us-east-1.rds.amazonaws.com' }],
    write: { host: 'perpmarkets.c3jgxn9bw7cv.us-east-1.rds.amazonaws.com' },
  },
  dialect: "postgres",
  logging: false,
  dialectOptions: {
    ssl: {
      require: true,
      rejectUnauthorized: false,
    },
  },
})

sequelize
  .authenticate()
  // @ts-ignore
  .then(function (err) {
    console.log("Connection has been established successfully.")
  })
  .catch(function (err) {
    console.log("Unable to connect to the database:", err)
  })

db.sequelize = sequelize
db.Sequelize = Sequelize

module.exports = db