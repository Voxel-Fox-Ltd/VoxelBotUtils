import vflbotutils

args = vflbotutils.runner.get_default_program_arguments()
shard_ids = vflbotutils.runner.validate_sharding_information(args)
bot = vflbotutils.Bot(shard_count=args.shard_count, shard_ids=shard_ids)
vflbotutils.runner.set_default_log_levels(bot, args)
vflbotutils.runner.run_bot(bot)
