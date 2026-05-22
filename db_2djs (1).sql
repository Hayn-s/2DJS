-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 22, 2026 at 01:05 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_2djs`
--

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `contact_num` varchar(15) DEFAULT NULL,
  `first_name` varchar(60) DEFAULT NULL,
  `middle_name` varchar(60) DEFAULT NULL,
  `last_name` varchar(60) DEFAULT NULL,
  `business_name` varchar(120) DEFAULT NULL,
  `is_business` tinyint(1) NOT NULL DEFAULT 0,
  `current_bal` decimal(10,2) NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `contact_num`, `first_name`, `middle_name`, `last_name`, `business_name`, `is_business`, `current_bal`) VALUES
(1, '09123456789', 'Juan', 'Dela', 'Cruz', NULL, 0, 4700.00),
(2, '09987654321', 'Maria', NULL, 'Santos', NULL, 0, 0.00),
(3, '09112223344', NULL, NULL, NULL, 'Lola Annie\'s Eatery', 1, 0.00),
(4, '09223334455', NULL, NULL, NULL, 'Kuya Ben Carinderia', 1, 0.00),
(5, '09334445566', NULL, NULL, NULL, 'Davao Chicken Reseller 01', 1, 0.00),
(6, '09445556677', NULL, NULL, NULL, 'Davao Chicken Reseller 02', 1, 0.00),
(7, '09556667788', NULL, NULL, NULL, 'Barangay 12 Market Stall', 1, 0.00),
(8, '09667778899', NULL, NULL, NULL, 'Golden Grill House', 1, 0.00),
(9, '09778889900', NULL, NULL, NULL, 'Mindanao Food Hub', 1, 0.00),
(10, NULL, 'Walk-in', NULL, 'Customer', NULL, 0, 0.00),
(11, '096967674201', 'Hev', 'Jammy Dela', 'Cruz', NULL, 0, 0.00),
(12, '09229529573', 'Mark', NULL, 'Jacox', NULL, 0, 0.00),
(13, '09912043825', 'John Michael', 'Deva', 'Flores', NULL, 0, 0.00),
(14, '09943728428', NULL, NULL, NULL, 'Kuya Bens Eatery', 1, 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `employees`
--

CREATE TABLE `employees` (
  `employee_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('Admin','Staff') NOT NULL,
  `date_hired` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employees`
--

INSERT INTO `employees` (`employee_id`, `name`, `username`, `password`, `role`, `date_hired`) VALUES
(1, 'Admin Heinz', 'Heinz', 'Heinz', 'Admin', '2026-04-23'),
(2, 'SJul', 'SJul', 'SJul', 'Staff', '2026-05-01'),
(3, 'Staff Jul', 'staff', 'staff', 'Staff', '2026-05-16');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `product_id` int(11) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `brand` varchar(50) DEFAULT NULL,
  `sku` varchar(50) DEFAULT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `stock_quantity` decimal(10,2) DEFAULT 0.00,
  `size` varchar(40) DEFAULT NULL,
  `reorder_point` decimal(10,2) NOT NULL DEFAULT 10.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`product_id`, `product_name`, `brand`, `sku`, `unit_price`, `stock_quantity`, `size`, `reorder_point`) VALUES
(1, 'Whole Dressed Chicken', 'HenHouse', 'SKU-00001', 180.00, 5.00, 'Small', 10.00),
(2, 'Chicken Drumstick', 'Farmers', 'ORG-WH-001', 190.00, 40.00, 'Regular', 10.00),
(3, 'Chicken Neck', 'SunriseFowl', 'SKU-00003', 200.00, 35.00, 'Small', 10.00),
(4, 'Whole Dressed Chicken', 'Magnolia', 'WH-MG-002', 195.00, 11.00, 'Large', 10.00),
(5, 'Chicken Breast Fillet', 'FarmFresh', 'SKU-00008', 220.00, 45.00, 'Large', 10.00),
(6, 'Choice Cuts: Breast', 'Magnolia', 'CC-BR-001', 210.00, 9.00, 'Jumbo', 10.00),
(7, 'Choice Cut: Breast Fillet (Purefoods)', 'Purefoods', 'CC-BRF-002', 220.00, 65.00, 'Regular', 10.00),
(8, 'Chicken Thigh', 'CluckGold', 'SKU-00011', 175.00, 20.00, 'Regular', 10.00),
(9, 'Choice Cuts: Thigh', 'Magnolia', 'CC-TH-005', 170.00, 3.00, 'Small', 10.00),
(10, 'Choice Cuts: Wings', 'Magnolia', 'CC-WG-002', 185.00, 0.00, 'Regular', 10.00),
(11, 'Chicken Drumstick', 'HenHouse', 'SKU-00015', 160.00, 5.00, 'Regular', 10.00),
(12, 'Chicken Leg Quarter', 'SunriseFowl', 'SKU-00016', 178.00, 12.00, 'Regular', 10.00),
(13, 'Chicken Liver', 'PrimePoultry', 'SKU-00017', 150.00, 20.00, 'Large', 10.00),
(14, 'Chicken Gizzard', 'MarketBird', 'SKU-00018', 155.00, 12.00, 'Small', 10.00),
(15, 'Gizzard/Liver Mix', 'AgriCorp', 'MIX-GZ-001', 158.00, 0.00, 'Regular', 10.00),
(16, 'Frozen Mixed Chicken Cuts', 'PrimePoultry', 'SKU-00020', 150.00, 0.00, 'Regular', 10.00);

-- --------------------------------------------------------

--
-- Table structure for table `sales`
--

CREATE TABLE `sales` (
  `sale_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  `pay_method` enum('Cash','Credit') NOT NULL,
  `sale_date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sales`
--

INSERT INTO `sales` (`sale_id`, `employee_id`, `customer_id`, `total_amount`, `pay_method`, `sale_date`) VALUES
(1, 1, 1, 4700.00, 'Credit', '2026-05-22 18:18:58'),
(2, 1, 2, 770.00, 'Cash', '2026-05-22 18:22:54');

--
-- Triggers `sales`
--
DELIMITER $$
CREATE TRIGGER `update_customer_balance` AFTER INSERT ON `sales` FOR EACH ROW BEGIN
                        IF NEW.pay_method = 'Credit' AND NEW.customer_id IS NOT NULL THEN
                            UPDATE customers
                            SET current_bal = current_bal + NEW.total_amount
                            WHERE customer_id = NEW.customer_id;
                        END IF;
                    END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `sale_items`
--

CREATE TABLE `sale_items` (
  `sale_item_id` int(11) NOT NULL,
  `sale_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `quantity` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sale_items`
--

INSERT INTO `sale_items` (`sale_item_id`, `sale_id`, `product_id`, `quantity`, `subtotal`) VALUES
(1, 1, 1, 5.00, 900.00),
(2, 1, 2, 20.00, 3800.00),
(3, 2, 6, 2.00, 420.00),
(4, 2, 8, 2.00, 350.00);

--
-- Triggers `sale_items`
--
DELIMITER $$
CREATE TRIGGER `after_sale_insert` AFTER INSERT ON `sale_items` FOR EACH ROW BEGIN
                        UPDATE products
                        SET stock_quantity = stock_quantity - NEW.quantity
                        WHERE product_id = NEW.product_id;
                    END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `stock_in`
--

CREATE TABLE `stock_in` (
  `stockin_id` int(11) NOT NULL,
  `batch_id` varchar(50) DEFAULT NULL,
  `product_id` int(11) NOT NULL,
  `supplier_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `quantity_kg` decimal(10,2) NOT NULL,
  `arrival_temp` decimal(5,2) NOT NULL,
  `date_received` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stock_in`
--

INSERT INTO `stock_in` (`stockin_id`, `batch_id`, `product_id`, `supplier_id`, `employee_id`, `quantity_kg`, `arrival_temp`, `date_received`) VALUES
(1, 'BATCH-20260518-88313', 1, 1, 1, 10.00, 2.00, '2026-05-18 21:02:02'),
(2, 'BATCH-20260518-95735', 2, 1, 1, 50.00, 2.00, '2026-05-18 21:17:04'),
(3, 'BATCH-20260518-68369', 3, 3, 1, 20.00, 2.00, '2026-05-18 21:24:57'),
(4, 'BATCH-20260518-17868', 3, 4, 1, 15.00, 4.00, '2026-05-18 21:25:29'),
(5, 'BATCH-20260518-85799', 4, 5, 1, 11.00, 5.00, '2026-05-18 21:42:54'),
(6, 'BATCH-20260518-44776', 5, 6, 1, 45.00, 3.00, '2026-05-18 21:43:14'),
(7, 'BATCH-20260518-75641', 6, 7, 1, 11.00, 1.00, '2026-05-18 21:43:44'),
(8, 'BATCH-20260518-50013', 7, 8, 1, 65.00, 2.00, '2026-05-18 21:43:58'),
(9, 'BATCH-20260518-22433', 8, 9, 1, 22.00, 4.00, '2026-05-18 21:47:46'),
(10, 'BATCH-20260518-69789', 9, 10, 1, 3.00, 3.00, '2026-05-18 21:47:59'),
(11, 'BATCH-20260519-19348', 11, 3, 1, 5.00, 3.00, '2026-05-19 07:18:20'),
(12, 'BATCH-20260519-27391', 12, 3, 1, 12.00, 5.00, '2026-05-19 07:18:34'),
(13, 'BATCH-20260519-39914', 13, 6, 1, 20.00, 3.00, '2026-05-19 07:18:46'),
(14, 'BATCH-20260519-41881', 14, 9, 1, 12.00, 3.00, '2026-05-19 07:18:54'),
(15, 'BATCH-20260522-32114', 2, 4, 1, 15.00, 3.00, '2026-05-22 18:13:16');

--
-- Triggers `stock_in`
--
DELIMITER $$
CREATE TRIGGER `check_chicken_temp` BEFORE INSERT ON `stock_in` FOR EACH ROW BEGIN
                        IF NEW.arrival_temp > 5.0 THEN
                            SIGNAL SQLSTATE '45000'
                            SET MESSAGE_TEXT = 'arrival temperature exceeds 7.0°C.';
                        END IF;
                    END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `stock_out`
--

CREATE TABLE `stock_out` (
  `stockout_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `employee_id` int(11) NOT NULL,
  `quantity_kg` decimal(10,2) NOT NULL,
  `reason` varchar(120) NOT NULL,
  `date_out` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stock_out`
--

INSERT INTO `stock_out` (`stockout_id`, `product_id`, `employee_id`, `quantity_kg`, `reason`, `date_out`) VALUES
(1, 2, 1, 3.00, 'Sold out', '2026-05-08 09:43:53'),
(2, 2, 1, 2.00, 'Spoilage/Expiry', '2026-05-19 07:20:24');

-- --------------------------------------------------------

--
-- Table structure for table `suppliers`
--

CREATE TABLE `suppliers` (
  `supplier_id` int(11) NOT NULL,
  `supplier_name` varchar(100) NOT NULL,
  `contact` varchar(50) NOT NULL,
  `address` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `suppliers`
--

INSERT INTO `suppliers` (`supplier_id`, `supplier_name`, `contact`, `address`) VALUES
(1, 'Magnolia Poultry Davao', '09112043825', 'Davao City'),
(2, 'Purefoods Davao Distributor', '09117356083', 'Davao City'),
(3, 'Farmers Fresh Chicken Supply', '09912273988', 'Davao City'),
(4, 'AgriCorp Poultry Supply', '09123456789', 'Davao City'),
(5, 'Davao Prime Poultry Trading', '09234567890', 'Davao City'),
(6, 'Mindanao Chicken Distributors', '09345678901', 'Davao City'),
(7, 'Southern Fresh Meats Supply', '09456789012', 'Davao City'),
(8, 'Davao Agro Poultry Hub', '09567890123', 'Davao City'),
(9, 'Golden Eggs & Poultry Supply', '09678901234', 'Davao City'),
(10, 'CityWide Chicken Supply Co.', '09789012345', 'Davao City');

-- --------------------------------------------------------

--
-- Stand-in structure for view `vw_detailed_sales`
-- (See below for the actual view)
--
CREATE TABLE `vw_detailed_sales` (
`transaction_id` int(11)
,`date_sold` datetime
,`employee_name` varchar(100)
,`customer_name` varchar(182)
,`customer_type` varchar(10)
,`item_name` varchar(100)
,`product_id` int(11)
,`qty_sold` decimal(10,2)
,`price_per_unit` decimal(10,2)
,`line_total` decimal(10,2)
,`sale_total` decimal(10,2)
,`payment_type` enum('Cash','Credit')
,`balance_impact` decimal(10,2)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `vw_inventory_status`
-- (See below for the actual view)
--
CREATE TABLE `vw_inventory_status` (
`product_id` int(11)
,`product_name` varchar(100)
,`brand` varchar(50)
,`size` varchar(40)
,`stock_quantity` decimal(10,2)
,`unit_price` decimal(10,2)
,`reorder_point` decimal(10,2)
,`stock_gap_kg` decimal(11,2)
,`last_stockin_date` datetime
,`last_sale_date` datetime
,`days_since_last_stockin` int(7)
,`availability_status` varchar(12)
,`status_priority` int(1)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `vw_supplier_safety_audit`
-- (See below for the actual view)
--
CREATE TABLE `vw_supplier_safety_audit` (
`stockin_id` int(11)
,`date_received` datetime
,`supplier_name` varchar(100)
,`product_name` varchar(100)
,`quantity_kg` decimal(10,2)
,`arrival_temp` decimal(5,2)
,`temp_breach_c` decimal(6,2)
,`safety_status` varchar(8)
,`action_level` varchar(9)
);

-- --------------------------------------------------------

--
-- Structure for view `vw_detailed_sales`
--
DROP TABLE IF EXISTS `vw_detailed_sales`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_detailed_sales`  AS SELECT `s`.`sale_id` AS `transaction_id`, `s`.`sale_date` AS `date_sold`, `e`.`name` AS `employee_name`, coalesce(case when `c`.`is_business` = 1 then `c`.`business_name` else trim(concat_ws(' ',`c`.`first_name`,`c`.`middle_name`,`c`.`last_name`)) end,'Walk-in Customer') AS `customer_name`, CASE WHEN `c`.`customer_id` is null THEN 'Walk-in' WHEN `c`.`is_business` = 1 THEN 'Business' ELSE 'Individual' END AS `customer_type`, `p`.`product_name` AS `item_name`, `p`.`product_id` AS `product_id`, `si`.`quantity` AS `qty_sold`, `p`.`unit_price` AS `price_per_unit`, `si`.`subtotal` AS `line_total`, `s`.`total_amount` AS `sale_total`, `s`.`pay_method` AS `payment_type`, CASE WHEN `s`.`pay_method` = 'Credit' THEN `s`.`total_amount` ELSE 0 END AS `balance_impact` FROM ((((`sales` `s` join `employees` `e` on(`e`.`employee_id` = `s`.`employee_id`)) left join `customers` `c` on(`s`.`customer_id` = `c`.`customer_id`)) join `sale_items` `si` on(`s`.`sale_id` = `si`.`sale_id`)) join `products` `p` on(`si`.`product_id` = `p`.`product_id`)) ;

-- --------------------------------------------------------

--
-- Structure for view `vw_inventory_status`
--
DROP TABLE IF EXISTS `vw_inventory_status`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_inventory_status`  AS SELECT `p`.`product_id` AS `product_id`, `p`.`product_name` AS `product_name`, `p`.`brand` AS `brand`, `p`.`size` AS `size`, `p`.`stock_quantity` AS `stock_quantity`, `p`.`unit_price` AS `unit_price`, `p`.`reorder_point` AS `reorder_point`, `p`.`stock_quantity`- `p`.`reorder_point` AS `stock_gap_kg`, (select max(`si`.`date_received`) from `stock_in` `si` where `si`.`product_id` = `p`.`product_id`) AS `last_stockin_date`, (select max(`s`.`sale_date`) from (`sale_items` `sli` join `sales` `s` on(`s`.`sale_id` = `sli`.`sale_id`)) where `sli`.`product_id` = `p`.`product_id`) AS `last_sale_date`, (select to_days(curdate()) - to_days(cast(max(`si`.`date_received`) as date)) from `stock_in` `si` where `si`.`product_id` = `p`.`product_id`) AS `days_since_last_stockin`, CASE WHEN `p`.`stock_quantity` <= 0 THEN 'Out of Stock' WHEN `p`.`stock_quantity` < coalesce(`p`.`reorder_point`,10) THEN 'Low Stock' ELSE 'In Stock' END AS `availability_status`, CASE WHEN `p`.`stock_quantity` <= 0 THEN 1 WHEN `p`.`stock_quantity` < coalesce(`p`.`reorder_point`,10) THEN 2 ELSE 3 END AS `status_priority` FROM `products` AS `p` ;

-- --------------------------------------------------------

--
-- Structure for view `vw_supplier_safety_audit`
--
DROP TABLE IF EXISTS `vw_supplier_safety_audit`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vw_supplier_safety_audit`  AS SELECT `st`.`stockin_id` AS `stockin_id`, `st`.`date_received` AS `date_received`, `sp`.`supplier_name` AS `supplier_name`, `p`.`product_name` AS `product_name`, `st`.`quantity_kg` AS `quantity_kg`, `st`.`arrival_temp` AS `arrival_temp`, CASE WHEN `st`.`arrival_temp` <= 5.0 THEN 0 ELSE round(`st`.`arrival_temp` - 5.0,2) END AS `temp_breach_c`, CASE WHEN `st`.`arrival_temp` <= 5.0 THEN 'Accepted' ELSE 'Rejected' END AS `safety_status`, CASE WHEN `st`.`arrival_temp` <= 5.0 THEN 'Compliant' WHEN `st`.`arrival_temp` <= 7.0 THEN 'Review' ELSE 'Critical' END AS `action_level` FROM ((`stock_in` `st` join `products` `p` on(`st`.`product_id` = `p`.`product_id`)) join `suppliers` `sp` on(`st`.`supplier_id` = `sp`.`supplier_id`)) ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `employees`
--
ALTER TABLE `employees`
  ADD PRIMARY KEY (`employee_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`product_id`),
  ADD UNIQUE KEY `sku` (`sku`);

--
-- Indexes for table `sales`
--
ALTER TABLE `sales`
  ADD PRIMARY KEY (`sale_id`),
  ADD KEY `fk_sale_employee` (`employee_id`),
  ADD KEY `fk_sale_customer` (`customer_id`);

--
-- Indexes for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD PRIMARY KEY (`sale_item_id`),
  ADD KEY `fk_item_sale` (`sale_id`),
  ADD KEY `fk_item_product` (`product_id`);

--
-- Indexes for table `stock_in`
--
ALTER TABLE `stock_in`
  ADD PRIMARY KEY (`stockin_id`),
  ADD UNIQUE KEY `batch_id` (`batch_id`),
  ADD KEY `fk_stock_product` (`product_id`),
  ADD KEY `fk_stock_supplier` (`supplier_id`),
  ADD KEY `fk_stock_employee` (`employee_id`);

--
-- Indexes for table `stock_out`
--
ALTER TABLE `stock_out`
  ADD PRIMARY KEY (`stockout_id`),
  ADD KEY `fk_stockout_product` (`product_id`),
  ADD KEY `fk_stockout_employee` (`employee_id`);

--
-- Indexes for table `suppliers`
--
ALTER TABLE `suppliers`
  ADD PRIMARY KEY (`supplier_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `employees`
--
ALTER TABLE `employees`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `product_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `sales`
--
ALTER TABLE `sales`
  MODIFY `sale_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `sale_items`
--
ALTER TABLE `sale_items`
  MODIFY `sale_item_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `stock_in`
--
ALTER TABLE `stock_in`
  MODIFY `stockin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `stock_out`
--
ALTER TABLE `stock_out`
  MODIFY `stockout_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `suppliers`
--
ALTER TABLE `suppliers`
  MODIFY `supplier_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `sales`
--
ALTER TABLE `sales`
  ADD CONSTRAINT `fk_sale_customer` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  ADD CONSTRAINT `fk_sale_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`);

--
-- Constraints for table `sale_items`
--
ALTER TABLE `sale_items`
  ADD CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `fk_item_sale` FOREIGN KEY (`sale_id`) REFERENCES `sales` (`sale_id`);

--
-- Constraints for table `stock_in`
--
ALTER TABLE `stock_in`
  ADD CONSTRAINT `fk_stock_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`),
  ADD CONSTRAINT `fk_stock_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`),
  ADD CONSTRAINT `fk_stock_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`supplier_id`);

--
-- Constraints for table `stock_out`
--
ALTER TABLE `stock_out`
  ADD CONSTRAINT `fk_stockout_employee` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`),
  ADD CONSTRAINT `fk_stockout_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
