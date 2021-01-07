-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 07, 2021 at 09:51 AM
-- Server version: 10.4.17-MariaDB
-- PHP Version: 7.3.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cs50`
--

-- --------------------------------------------------------

--
-- Table structure for table `appliances`
--

CREATE TABLE `appliances` (
  `app_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `power` float NOT NULL,
  `duration` float NOT NULL,
  `frequency` varchar(255) NOT NULL,
  `daily_usage` float NOT NULL,
  `monthly_usage` float NOT NULL,
  `daily_cost` float NOT NULL,
  `monthly_cost` float NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `appliances`
--

INSERT INTO `appliances` (`app_id`, `user_id`, `name`, `type`, `power`, `duration`, `frequency`, `daily_usage`, `monthly_usage`, `daily_cost`, `monthly_cost`, `created_at`, `updated_at`) VALUES
(1, 2, 'AC', 'Cooling', 4, 4, 'Daily', 0.02, 0.48, 0.18, 5.43, '2021-01-05 14:47:58', '2021-01-05 14:47:58'),
(2, 2, 'Bulb', 'Lighting', 5, 8, 'Daily', 0.04, 1.2, 0.45, 13.58, '2021-01-05 14:49:18', '2021-01-05 14:49:18'),
(4, 2, 'Computer', 'Entertainment', 10, 18, 'Daily', 0.18, 5.4, 2.04, 61.13, '2021-01-05 14:50:50', '2021-01-05 14:50:50'),
(9, 2, 'Rice cooker', 'Kitchen Appliances', 100, 26, 'Daily', 2.6, 78, 29.43, 882.96, '2021-01-07 06:08:55', '2021-01-07 06:08:55'),
(10, 2, 'Vacuum', 'Household Appliances', 120, 24, 'Daily', 2.88, 86.4, 32.6, 978.05, '2021-01-07 06:09:38', '2021-01-07 06:09:38'),
(12, 2, 'TV', 'Entertainment', 12, 7, 'Daily', 0.08, 2.52, 0.91, 28.53, '2021-01-07 06:22:18', '2021-01-07 06:22:18'),
(13, 2, 'TV', 'Entertainment', 12, 7, 'Daily', 0.08, 2.52, 0.91, 28.53, '2021-01-07 06:22:18', '2021-01-07 06:22:18'),
(14, 2, 'Fan', 'Cooling', 12, 12, 'Weekly', 0.02, 0.58, 0.23, 6.57, '2021-01-07 06:22:32', '2021-01-07 06:22:32'),
(15, 3, 'Smart TV', 'Entertainment', 10, 12, 'Daily', 0.12, 3.6, 1.36, 40.75, '2021-01-07 06:28:50', '2021-01-07 06:28:50');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `cost_limit` float NOT NULL DEFAULT 1000,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `name`, `email`, `password`, `cost_limit`, `created_at`, `updated_at`) VALUES
(2, 'Arya Stark', 'arya@gmail.com', 'pbkdf2:sha256:150000$Tx8lc70a$9724dab7d3e076da0b0a0a87fc46c9534a8755443f70ce6c505f43db9aa75858', 1000, '2021-01-05 10:50:06', '2021-01-05 10:50:06'),
(3, 'Gabriela Balisacan', 'gab@gmail.com', 'pbkdf2:sha256:150000$qXtLW8gr$cbdd3f0772fad9173053a145cd4c5690e36e44488685f7cfa9c9445c45b9f20b', 1000, '2021-01-07 06:26:34', '2021-01-07 06:26:34');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appliances`
--
ALTER TABLE `appliances`
  ADD PRIMARY KEY (`app_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appliances`
--
ALTER TABLE `appliances`
  MODIFY `app_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
